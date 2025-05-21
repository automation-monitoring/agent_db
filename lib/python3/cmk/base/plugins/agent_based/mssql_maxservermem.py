#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)
from .agent_based_api.v1 import Result, State, Service, Metric, register

import pprint

defaults_mssql_maxservermem = {}


def parse_mssql_maxservermem(string_table):
    # Example output
    # [['DB', '2147483647', 'Maximum size of server memory (MB)']]
    db, val, desc = string_table[0]
    return {"value": int(val), "description": desc}


register.agent_section(
    name="mssql_maxservermem",
    parse_function=parse_mssql_maxservermem,
)


def discover_mssql_maxservermem(section):
    if len(section) > 0:
        yield Service()


def check_mssql_maxservermem(params, section):
    value = section["value"]
    description = section["description"]
    # Parameters({'maxservermem': 2500}
    if not "maxservermem" in params:
        state = State.OK
        summary = f"{value} MB - informational only"
    else:
        maxservermem = params["maxservermem"]
        if maxservermem == value:
            state = State.OK
            summary = f"{value} MB"
        else:
            state = State.CRIT
            summary = f"{value} MB (!= {maxservermem} MB)"

    yield Result(state=state, summary=summary)


register.check_plugin(
    name="mssql_maxservermem",
    sections=["mssql_maxservermem"],
    service_name="MSSQL Max Server Memory",
    discovery_function=discover_mssql_maxservermem,
    check_function=check_mssql_maxservermem,
    check_default_parameters=defaults_mssql_maxservermem,
    check_ruleset_name="mssql_maxservermem",
)
