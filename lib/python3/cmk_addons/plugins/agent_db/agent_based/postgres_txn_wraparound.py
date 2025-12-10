#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    check_levels,
    Service,
    render,
)


def parse_postgres_txn_wraparound(string_table):
    section = {}
    instance = None
    for line in string_table:
        if line[0][:3] == "[[[" and line[0][-3:] == "]]]":
            instance = line[0][3:-3].upper()
            continue
        if line == ['datname', 'age']:
            continue
        db_name = line[0]
        try:
            unfrozen_txns = int(line[1])
        except ValueError:
            continue
        section[f"{instance}/{db_name}"] = unfrozen_txns
    return section


agent_section_postgres_txn_wraparound = AgentSection(
    name="postgres_txn_wraparound",
    parse_function=parse_postgres_txn_wraparound,
)


def discover_postgres_txn_wraparound(section):
    for db in section:
        yield Service(item=db)


def check_postgres_txn_wraparound(item, params, section):
    unfrozen_txns = section[item]
    levels = params.get("unfrozen_txns")
    yield from check_levels(
                value=unfrozen_txns,
                levels_upper=params.get("unfrozen_txns"),
                metric_name="unfrozen_txns",
                render_func=lambda v: f"{v} XIDs",
            )


check_plugin_postgres_txn_wraparound = CheckPlugin(
    name="postgres_txn_wraparound",
    service_name="PostgreSQL Transaction Wraparound %s",
    discovery_function=discover_postgres_txn_wraparound,
    check_function=check_postgres_txn_wraparound,
    check_default_parameters={
        "unfrozen_txns" : ("fixed", (1300000000, 1400000000)),
    },
    check_ruleset_name="postgres_txn_wraparound",
)
