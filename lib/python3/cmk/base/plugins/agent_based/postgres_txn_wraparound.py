#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Service,
    State,
    Metric,
    Result,
    register,
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


register.agent_section(
    name="postgres_txn_wraparound",
    parse_function=parse_postgres_txn_wraparound,
)


def discover_postgres_txn_wraparound(section):
    for db in section:
        yield Service(item=db)


def check_postgres_txn_wraparound(item, params, section):
    unfrozen_txns = section[item]
    levels = params.get("unfrozen_txns")
    infotext = f"{unfrozen_txns} XIDs"
    yield Metric("unfrozen_txns", unfrozen_txns, levels=levels)
    if levels:
        warn, crit = levels
        levelstext = f" (warn/crit at {warn}/{crit})"
        if unfrozen_txns >= crit:
            yield Result(state=State.CRIT, summary=infotext + levelstext)
        elif unfrozen_txns >= warn:
            yield Result(state=State.WARN, summary=infotext + levelstext)
        else:
            yield Result(state=State.OK, summary=infotext)
    else:
        yield Result(state=State.OK, summary=infotext)


register.check_plugin(
    name="postgres_txn_wraparound",
    service_name="PostgreSQL Transaction Wraparound %s",
    discovery_function=discover_postgres_txn_wraparound,
    check_function=check_postgres_txn_wraparound,
    check_default_parameters={
        "unfrozen_txns" : (1300000000, 1400000000)
    },
    check_ruleset_name="postgres_txn_wraparound",
)
