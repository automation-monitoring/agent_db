#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Optional, TypedDict

from cmk.agent_based.v2 import (
    AgentSection,
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    LevelsT,
    render,
    Result,
    Service,
    State,
    StringTable,
)

import json


@dataclass(frozen=True)
class DbConnectionData:
    connection_time: float
    error: Optional[str] = None


Section = Mapping[str, DbConnectionData]


def parse_db_connection_time(string_table: StringTable) -> Section:
    """Parse database connection time data from agent output.
    
    Example data:
        [['{"db_cstr":', '"projdat",', '"connection_time":', '0.008624076843261719,', '"error":', 'null}'],
         ['{"db_cstr":', '"master",', '"connection_time":', '0.006785392761230469,', '"error":', 'null}']]
    """
    parsed: dict[str, DbConnectionData] = {}
    
    for line in string_table:
        try:
            # Join the fragmented JSON string
            json_string = " ".join(line)
            # Parse the JSON string
            loaded_data = json.loads(json_string)

            # Extract the relevant information from the JSON
            db_name = loaded_data["db_cstr"]
            connection_time = float(loaded_data["connection_time"])
            error = loaded_data.get("error")
            
            # Store None instead of null string
            if error == "null" or error is None:
                error = None

            # Store the data in the result dictionary
            parsed[db_name] = DbConnectionData(
                connection_time=connection_time,
                error=error,
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            # Skip malformed entries
            continue

    return parsed


def discover_db_connection_time(section: Section) -> DiscoveryResult:
    """Discover a service for each database."""
    for db_cstr in section:
        yield Service(item=db_cstr)


class Params(TypedDict):
    db_cursor_avail_sec: LevelsT[float]


def check_db_connection_time(item: str, params: Params, section: Section) -> CheckResult:
    """Check database connection time against thresholds."""
    if item not in section:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Database {item} not found in agent output",
        )
        return

    data = section[item]
    
    # Check for connection errors first
    if data.error:
        yield Result(
            state=State.CRIT,
            summary=f"Unable to connect to database {item}",
            details=str(data.error),
        )
        return

    # Check connection time against levels
    yield from check_levels(
        data.connection_time,
        metric_name="db_connect_time",
        levels_upper=params["db_cursor_avail_sec"],
        label="Connection time",
        render_func=render.timespan,
    )


# Register agent sections for each database type
agent_section_mysql_connection_time = AgentSection(
    name="mysql_connection_time",
    parse_function=parse_db_connection_time,
)

agent_section_oracle_connection_time = AgentSection(
    name="oracle_connection_time",
    parse_function=parse_db_connection_time,
)

agent_section_mssql_connection_time = AgentSection(
    name="mssql_connection_time",
    parse_function=parse_db_connection_time,
)

agent_section_postgres_connection_time = AgentSection(
    name="postgres_connection_time",
    parse_function=parse_db_connection_time,
)


# Register check plugins for each database type
check_plugin_mssql_connection_time = CheckPlugin(
    name="mssql_connection_time",
    service_name="MSSQL DB Connect %s",
    discovery_function=discover_db_connection_time,
    check_function=check_db_connection_time,
    check_ruleset_name="db_connection_time",
    check_default_parameters={"db_cursor_avail_sec": ("fixed",(1.5, 3.0))},
)

check_plugin_mysql_connection_time = CheckPlugin(
    name="mysql_connection_time",
    service_name="MySQL DB Connect %s",
    discovery_function=discover_db_connection_time,
    check_function=check_db_connection_time,
    check_ruleset_name="db_connection_time",
    check_default_parameters={"db_cursor_avail_sec": ("fixed",(1.5, 3.0))},
)

check_plugin_oracle_connection_time = CheckPlugin(
    name="oracle_connection_time",
    service_name="ORA DB Connect %s",
    discovery_function=discover_db_connection_time,
    check_function=check_db_connection_time,
    check_ruleset_name="db_connection_time",
    check_default_parameters={"db_cursor_avail_sec": ("fixed",(1.5, 3.0))},
)

check_plugin_postgres_connection_time = CheckPlugin(
    name="postgres_connection_time",
    service_name="PostgreSQL DB Connect %s",
    discovery_function=discover_db_connection_time,
    check_function=check_db_connection_time,
    check_ruleset_name="db_connection_time",
    check_default_parameters={"db_cursor_avail_sec": ("fixed",(1.5, 3.0))},
)
