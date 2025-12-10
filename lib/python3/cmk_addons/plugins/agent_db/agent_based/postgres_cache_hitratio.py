#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    check_levels,
    Service,
    render,
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


agent_section_postgres_cache_hitratio = AgentSection(
    name="postgres_cache_hitratio",
    parse_function=parse_postgres_cache_hitratio,
)


def discover_postgres_cache_hitratio(section):
    for db in section:
        yield Service(item=db)


def check_postgres_cache_hitratio(item, params, section):
    hitratio = section[item]
    yield from check_levels(
                value=hitratio,
                levels_lower=params.get("levels_lower"),
                metric_name="data_hitratio",
                render_func=render.percent,
            )


check_plugin_postgres_cache_hitratio = CheckPlugin(
    name="postgres_cache_hitratio",
    service_name="PostgreSQL Cache Hitratio %s",
    discovery_function=discover_postgres_cache_hitratio,
    check_function=check_postgres_cache_hitratio,
    check_default_parameters={},
    check_ruleset_name="postgres_cache_hitratio",
)
