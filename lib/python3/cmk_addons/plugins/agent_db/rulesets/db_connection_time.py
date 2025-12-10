#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

from cmk.rulesets.v1 import Help, rule_specs, Title
from cmk.rulesets.v1.form_specs import (
    Dictionary,
    DictElement,
    DefaultValue,
    LevelDirection,
    migrate_to_float_simple_levels,
    SimpleLevels,
    String,
    TimeMagnitude,
    TimeSpan,
)


def _parameter_formspec_db_connection_time():
    return Dictionary(
        title=Title("Database connection time levels"),
        elements={
            "db_cursor_avail_sec": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Connection time"),
                    help_text=Help(
                        "Set the upper levels for the time it takes to establish "
                        "a database connection. The connection time is measured from "
                        "the moment the connection is requested until the database "
                        "responds with a successful connection."
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue((2.5, 5.0)),
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[
                            TimeMagnitude.SECOND,
                            TimeMagnitude.MILLISECOND,
                        ]
                    ),
                    migrate=migrate_to_float_simple_levels,
                ),
                required=True,
            ),
        },
    )


def _item_spec() -> String:
    return String(
        help_text=Help("Specify the database name that the rule should apply to."),
    )


rule_spec_db_connection_time = rule_specs.CheckParameters(
    title=Title("Database connection time"),
    topic=rule_specs.Topic.APPLICATIONS,
    name="db_connection_time",
    parameter_form=_parameter_formspec_db_connection_time,
    condition=rule_specs.HostAndItemCondition(
        item_title=Title("Database name"),
        item_form=_item_spec(),
    ),
)
