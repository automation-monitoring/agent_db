#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    Metric,
    Result,
    State,
    Service,
)


def parse_oracle_version_v2(string_table):
    # ['XEPDB1',
    # 'Oracle',
    # 'Database',
    # '21c',
    # 'Express',
    # 'Edition',
    # 'Release',
    # '21.0.0.0.0',
    # '-',
    # 'Production']
    # ['PDB2',
    # 'Oracle',
    # 'Database',
    # '21c',
    # 'Express',
    # 'Edition',
    # 'Release',
    # '21.0.0.0.0',
    # '-',
    # 'Production']
    ret = {}
    for line in string_table:
        # first word  = dict key
        db = line[0]
        # everything after first word = dict value
        ret[db] = " ".join(line[1:])
    return ret


agent_section_oracle_version_v2 = AgentSection(
    name="oracle_version_v2",
    parse_function=parse_oracle_version_v2,
)


def discover_oracle_version_v2(section):
    for db in section.keys():
        yield Service(item=db)


def check_oracle_version_v2(item, section):
    state = State.OK
    # state = State.WARN
    # state = State.CRIT
    # state = State.UNKNOWN
    # yield Metric("uptime",uptime)
    # yield Metric(name="CPU", value=value, levels=(80,90))
    # yield Metric(name="CPU", value=value, levels=(80,90), boundaries=(0,100))

    # yield Result(state=state, summary=infotext)
    # before:
    # perf = [
    #    ("uptime", uptime),
    # ]

    # loop over all output lines of the agent
    for db, version in section.items():
        if item == db:
            yield Result(state=state, summary=version)


check_plugin_oracle_version_v2 = CheckPlugin(
    name="oracle_version_v2",
    service_name="ORA %s Oracle Version",
    discovery_function=discover_oracle_version_v2,
    check_function=check_oracle_version_v2,
)
