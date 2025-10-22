#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

from cmk.graphing.v1 import graphs, metrics, perfometers, Title

UNIT_TIME = metrics.Unit(metrics.TimeNotation())

metric_db_connect_time = metrics.Metric(
    name="db_connect_time",
    title=Title("Connection time"),
    unit=UNIT_TIME,
    color=metrics.Color.BLUE,
)

graph_db_connection_time = graphs.Graph(
    name="db_connection_time",
    title=Title("Database connection time"),
    simple_lines=[
        "db_connect_time",
    ],
)

perfometer_db_connection_time = perfometers.Perfometer(
    name="db_connection_time",
    focus_range=perfometers.FocusRange(
        perfometers.Closed(0),
        perfometers.Closed(3),
    ),
    segments=["db_connect_time"],
)
