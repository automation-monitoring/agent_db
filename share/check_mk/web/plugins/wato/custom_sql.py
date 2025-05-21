#!/usr/bin/env python3

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)

from cmk.gui.valuespec import (
    Dictionary,
    Float,
    RegExp,
    TextInput,
    Tuple,
)

def _item_spec_custom_sql():
    return TextInput(
            title=_("Service name")
        )


def _parameter_valuespec_custom_sql_string():
    return Dictionary(
            elements=[
                (
                    "expected_regex",
                    RegExp(
                        title=_("String to expect (RegEx)"),
                        mode=RegExp.infix,
                    )
                ),
            ]
        )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        group=RulespecGroupCheckParametersApplications,
        check_group_name="custom_sql_string",
        title=lambda: _("Custom SQL: String"),
        item_spec=_item_spec_custom_sql,
        parameter_valuespec=_parameter_valuespec_custom_sql_string,
        match_type="dict",
    )
)


def _parameter_valuespec_custom_sql_number():
    return Dictionary(
            elements=[
                (
                    "levels_upper",
                    Tuple(
                        title=_("Upper levels"),
                        elements=[
                            Float(title=_("Warning at")),
                            Float(title=_("Critical at")),
                        ],
                    ),
                ),
                (
                    "levels_lower",
                    Tuple(
                        title=_("Lower levels"),
                        elements=[
                            Float(title=_("Warning below")),
                            Float(title=_("Critical below")),
                        ],
                    ),
                ),
            ]
        )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        group=RulespecGroupCheckParametersApplications,
        check_group_name="custom_sql_number",
        title=lambda: _("Custom SQL: Number"),
        item_spec=_item_spec_custom_sql,
        parameter_valuespec=_parameter_valuespec_custom_sql_number,
        match_type="dict",
    )
)
