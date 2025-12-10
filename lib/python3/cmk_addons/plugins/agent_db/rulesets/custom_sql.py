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
    Float,
    LevelDirection,
    MatchingScope,
    migrate_to_float_simple_levels,
    RegularExpression,
    SimpleLevels,
)


def _parameter_formspec_custom_sql_string():
    return Dictionary(
        title=Title("Custom SQL string parameters"),
        elements={
            "expected_regex": DictElement(
                parameter_form=RegularExpression(
                    title=Title("String to expect (RegEx)"),
                    help_text=Help(
                        "Define a regular expression that the SQL result string should match. "
                        "If the pattern doesn't match, the check will return a CRITICAL state."
                    ),
                    predefined_help_text=MatchingScope.INFIX,
                ),
                required=False,
            ),
        },
    )


def _parameter_formspec_custom_sql_number():
    return Dictionary(
        title=Title("Custom SQL number parameters"),
        elements={
            "levels_upper": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Upper levels"),
                    help_text=Help(
                        "Set upper thresholds for the numeric SQL result. "
                        "The check will warn or go critical if the value exceeds these levels."
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue((80.0, 90.0)),
                    form_spec_template=Float(),
                    migrate=migrate_to_float_simple_levels,
                ),
                required=False,
            ),
            "levels_lower": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Lower levels"),
                    help_text=Help(
                        "Set lower thresholds for the numeric SQL result. "
                        "The check will warn or go critical if the value falls below these levels."
                    ),
                    level_direction=LevelDirection.LOWER,
                    prefill_fixed_levels=DefaultValue((10.0, 5.0)),
                    form_spec_template=Float(),
                    migrate=migrate_to_float_simple_levels,
                ),
                required=False,
            ),
        },
    )


rule_spec_custom_sql_string = CheckParameters(
    title=Title("Custom SQL: String"),
    topic=Topic.APPLICATIONS,
    name="custom_sql_string",
    parameter_form=_parameter_formspec_custom_sql_string,
    condition=HostAndItemCondition(item_title=Title("Service name")),
)

rule_spec_custom_sql_number = CheckParameters(
    title=Title("Custom SQL: Number"),
    topic=Topic.APPLICATIONS,
    name="custom_sql_number",
    parameter_form=_parameter_formspec_custom_sql_number,
    condition=HostAndItemCondition(item_title=Title("Service name")),
)
