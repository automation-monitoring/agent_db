#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

from .agent_based_api.v1 import Result, State, Service, Metric, register
import json

defaults_agent_db_stats = {"runtime_levels": (10.0, 30.0)}


def parse_agent_db_stats(string_table):
    ret = {}
    for line in string_table:

        try:
            # Attempt to parse the JSON string
            loaded_data = json.loads(line[0])

            # Iterate through keys (database names) in the loaded JSON data
            for db_name, stats in loaded_data.items():
                if db_name not in ret:
                    ret[db_name] = {}
                ret[db_name].update(stats)

            # pprint.pprint(loaded_data)
            # ret.update(loaded_data)
        except json.JSONDecodeError as e:
            # Handle the JSON decoding error
            print(f"Error decoding JSON: {e}")

    # pprint.pprint(ret)
    return ret


register.agent_section(
    name="agent_db_stats",
    parse_function=parse_agent_db_stats,
)


def discover_agent_db_stats(section):
    # if len(section) > 0:
    #    yield Service()
    for db_cstr in section.keys():
        # print(db_cstr)
        yield Service(item=db_cstr)


def check_agent_db_stats(item, params, section):
    try:
        section = section[item]
    except KeyError:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Database '{item}' not found in agent output, maybe removed?",
        )
        return

    exceptions = []
    details = None
    state = None
    # for line in section:
    for statement, stats in section.items():
        if stats["exception"] is not None:
            exceptions.append(f"{statement}: {stats['exception']}")
        if stats["runtime"] is not None:
            warn, crit = params["runtime_levels"]
            if stats["runtime"] >= crit:
                state = State.CRIT
            elif stats["runtime"] >= warn:
                state = State.WARN
            yield Metric(
                name=f"query_runtime_{statement}",
                value=stats["runtime"],
                levels=params["runtime_levels"],
            )
    if len(exceptions) > 0:
        state = State.CRIT
        summary = f"{len(exceptions)} of {len(section)} statements failed. See details for more information"
        details = "\n".join(exceptions)
    else:
        state = State.OK
        summary = f"All ({len(section)}) statements executed successfully"

    if details:
        yield Result(state=state, summary=summary, details=details)
    else:
        yield Result(state=state, summary=summary)


register.check_plugin(
    name="agent_db_stats",
    sections=["agent_db_stats"],
    service_name="Agent DB Stats %s",
    discovery_function=discover_agent_db_stats,
    check_function=check_agent_db_stats,
    check_default_parameters=defaults_agent_db_stats,
    check_ruleset_name="agent_db_stats",
)
