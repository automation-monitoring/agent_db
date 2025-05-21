#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Service,
    State,
    Metric,
    Result,
    register,
)


# NOTE: This is the Blocks hitratio! (sd.blks_hit in relation to reads)

def parse_postgres_cache_hitratio(string_table):
    section = {}
    instance = None
    for line in string_table:
        if line[0][:3] == "[[[" and line[0][-3:] == "]]]":
            instance = line[0][3:-3].upper()
            continue
        if line == ['dhitratio', 'datname', 'rolname']:
            continue
        db_name = line[1]
        try:
           hitratio  = float(line[0])
        except ValueError:
            continue
        section[f"{instance}/{db_name}"] = hitratio
    return section


register.agent_section(
    name="postgres_cache_hitratio",
    parse_function=parse_postgres_cache_hitratio,
)


def discover_postgres_cache_hitratio(section):
    for db in section:
        yield Service(item=db)


def check_postgres_cache_hitratio(item, params, section):
    hitratio = section[item]
    infotext = f"{hitratio:.2f}%"
    levels = params.get("levels_lower")
    yield Metric("data_hitratio", hitratio, levels=levels)
    if levels:
        warn, crit = levels
        levelstext = f" (warn/crit below {warn:.2f}%/{crit:.2f}%)"
        if hitratio < crit:
            yield Result(state=State.CRIT, summary=infotext + levelstext)
        elif hitratio < warn:
            yield Result(state=State.WARN, summary=infotext + levelstext)
        else:
            yield Result(state=State.OK, summary=infotext)
    else:
        yield Result(state=State.OK, summary=infotext)


register.check_plugin(
    name="postgres_cache_hitratio",
    service_name="PostgreSQL Cache Hitratio %s",
    discovery_function=discover_postgres_cache_hitratio,
    check_function=check_postgres_cache_hitratio,
    check_default_parameters={},
    check_ruleset_name="postgres_cache_hitratio",
)
