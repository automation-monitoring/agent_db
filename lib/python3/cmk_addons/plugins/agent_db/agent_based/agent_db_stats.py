#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

from cmk.agent_based.v2 import (
    AgentSection,
    check_levels,
    CheckPlugin,
    render,
    Result,
    Service,
    State,
)

import json


def parse_agent_db_stats(string_table):
    """Parse database statistics data from agent output."""
    parsed = {}
    for line in string_table:
        try:
            # Attempt to parse the JSON string
            loaded_data = json.loads(line[0])

            # Iterate through keys (database names) in the loaded JSON data
            for db_name, stats in loaded_data.items():
                if db_name not in parsed:
                    parsed[db_name] = {}
                parsed[db_name].update(stats)

        except (json.JSONDecodeError, IndexError, KeyError):
            # Skip malformed entries
            continue

    return parsed


def discover_agent_db_stats(section):
    """Discover a service for each database."""
    for db_cstr in section.keys():
        yield Service(item=db_cstr)


def check_agent_db_stats(item, params, section):
    """Check the database stats for a specific database."""
    if item not in section:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Database '{item}' not found in agent output, maybe removed?",
        )
        return

    db_section = section[item]
    exceptions = []

    # Check each statement in the database
    for statement, stats in db_section.items():
        # Handle exceptions
        if stats["exception"] is not None:
            exceptions.append(f"{statement}: {stats['exception']}")
            continue

        # Handle runtime checks with levels
        if stats["runtime"] is not None:
            levels = params["runtime_levels"]

            yield from check_levels(
                stats["runtime"],
                metric_name=f"query_runtime_{statement}",
                levels_upper=levels,
                label=f"Runtime {statement}",
                render_func=render.timespan,
                notice_only=True,
            )

    # Overall service state based on exceptions
    if len(exceptions) > 0:
        yield Result(
            state=State.CRIT,
            summary=f"{len(exceptions)} of {len(db_section)} statements failed. See details for more information",
            details="\n".join(exceptions),
        )
    else:
        yield Result(
            state=State.OK,
            summary=f"All ({len(db_section)}) statements executed successfully",
        )


# Register agent section
agent_section_agent_db_stats = AgentSection(
    name="agent_db_stats",
    parse_function=parse_agent_db_stats,
)

# Register check plugin
check_plugin_agent_db_stats = CheckPlugin(
    name="agent_db_stats",
    service_name="Agent DB Stats %s",
    discovery_function=discover_agent_db_stats,
    check_function=check_agent_db_stats,
    check_ruleset_name="agent_db_stats",
    check_default_parameters={"runtime_levels": ("fixed", (10.0, 30.0))},
)
