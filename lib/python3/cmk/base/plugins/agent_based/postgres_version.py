#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

# Checkmk have removed the check postgres_version in version 2.3 (cf. Werk #15078)
# The functionality has been included in the postgres_instances check.
# In our case, this does not work, as postgres_instances requires PIDs, that we
# do not have as we do not query locally.
# To include the functionality of postgres_version also for 2.3 and up, we add
# this check that only discovers services in the following cases:
#   * In Checkmk version 2.2
#   * In other Checkmk versions if the section agent_db_stats is not empty (ie it's agent_db)

from .agent_based_api.v1 import Result, State, Service, register
try:
    from cmk.utils.version import __version__
except ImportError:
    __version__ = "Not 2.2"


# Checkmk 2.3 no longer has the file postgres_version.py, but rather
# defines this section together with postgres_instances, causing the
# package to not work as the postgres_version section is already registered.
# This is why we need this conditional.

if __version__.startswith("2.2"):
    def parse_postgres_version(string_table):
        parsed = {}
        instance_name = ""
        for line in string_table:
            if line[0].startswith("[[[") and line[0].endswith("]]]"):
                instance_name = line[0][3:-3]
                continue
            parsed.setdefault(instance_name, " ".join(line))
        return parsed


    register.agent_section(
        name="postgres_version",
        parse_function=parse_postgres_version,
    )


def discover_postgres_version(section_postgres_version, section_agent_db_stats):
    if not section_postgres_version:
        return
    if not __version__.startswith("2.2") and not section_agent_db_stats:
        return
    for instance in section_postgres_version:
        yield Service(item=instance)


def check_postgres_version(item, section_postgres_version, section_agent_db_stats):
    data = section_postgres_version.get(item)
    if data is None:
        return
    if "could not connect" in data:
        yield Result(state=State.UNKNOWN, summary="Login into database failed")
        return
    yield Result(state=State.OK, summary=data)


register.check_plugin(
    name="postgres_version",
    sections=["postgres_version", "agent_db_stats"],
    service_name="PostgreSQL Version %s",
    discovery_function=discover_postgres_version,
    check_function=check_postgres_version,
)
