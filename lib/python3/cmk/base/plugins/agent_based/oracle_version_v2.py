#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# from .agent_based_api.v1 import Result, State, Service, Metric, register
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Result,
    State,
    Service,
    Metric,
    register,
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


register.agent_section(
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


register.check_plugin(
    name="oracle_version_v2",
    # sections=["oracle_version_v2"],
    service_name="ORA %s Oracle Version",
    discovery_function=discover_oracle_version_v2,
    check_function=check_oracle_version_v2,
    # check_default_parameters=defaults_oracle_version_v2,
    # check_default_parameters=None,
    # check_ruleset_name="oracle_version_v2",
)
