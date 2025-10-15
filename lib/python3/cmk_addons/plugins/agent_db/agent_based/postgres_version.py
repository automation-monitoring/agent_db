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
# this check that only discovers services if the section agent_db_stats is not empty (ie it's agent_db)

from cmk.agent_based.v2 import Result, State, Service, CheckPlugin

# Checkmk 2.3 no longer has the file postgres_version.py, but rather
# defines this section together with postgres_instances

def discover_postgres_version(section_postgres_version, section_agent_db_stats):
    if not section_postgres_version:
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


check_plugin_postgres_version = CheckPlugin(
    name="postgres_version",
    sections=["postgres_version", "agent_db_stats"],
    service_name="PostgreSQL Version %s",
    discovery_function=discover_postgres_version,
    check_function=check_postgres_version,
)
