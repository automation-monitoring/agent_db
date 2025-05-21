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
    TextInput,
    Tuple,
    Transform,
)


def _item_spec_agent_db_stats():
    return TextInput(
        title=_("DB"),
    )


def _parameter_valuespec_agent_db_stats():
    return Dictionary(
        elements=[
            (
                "runtime_levels",
                Tuple(
                    title=_("Query runtime"),
                    help=_("These levels are applied to all queries"),
                    elements=[
                        Transform(
                            valuespec=Float(title=_("Warning at"), unit="ms"),
                            to_valuespec=lambda v: v * 1000,
                            from_valuespec=lambda v: v / 1000,
                        ),
                        Transform(
                            valuespec=Float(title=_("Critical at"), unit="ms"),
                            to_valuespec=lambda v: v * 1000,
                            from_valuespec=lambda v: v / 1000,
                        ),
                    ],
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        group=RulespecGroupCheckParametersApplications,
        check_group_name="agent_db_stats",
        title=lambda: _("Agent DB Stats"),
        item_spec=_item_spec_agent_db_stats,
        parameter_valuespec=_parameter_valuespec_agent_db_stats,
        match_type="dict",
    )
)
