#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    Topic,
    HostAndItemCondition,
)

from cmk.rulesets.v1.form_specs import (
    Dictionary,
    DictElement,
    DefaultValue,
    LevelDirection,
    migrate_to_float_simple_levels,
    SimpleLevels,
    TimeMagnitude,
    TimeSpan,
)


def _parameter_formspec_agent_db_stats():
    return Dictionary(
        title=Title("Database query runtime levels"),
        elements={
            "runtime_levels": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Query runtime"),
                    help_text=Help(
                        "Set the upper levels for database query execution time. "
                        "These levels are applied to all queries executed by the agent_db special agent."
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue((10.0, 30.0)),
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


rule_spec_agent_db_stats = CheckParameters(
    title=Title("Database query statistics"),
    topic=Topic.APPLICATIONS,
    name="agent_db_stats",
    parameter_form=_parameter_formspec_agent_db_stats,
    condition=HostAndItemCondition(item_title=Title("Database name")),
)
