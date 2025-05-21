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


def _item_spec_db_connection_time():
    return TextInput(
                title=_("DB"),
            )


def _parameter_valuespec_db_connection_time():
    return Dictionary(
                elements=[
                    ("db_cursor_avail_sec",
                     Tuple(
                         title=_("DB Connection Time"),
                         elements=[
                             Transform(
                                valuespec=Float(title=_("Warning at"), unit="ms"),
                                to_valuespec=lambda v: v*1000,
                                from_valuespec=lambda v: v/1000,
                             ),
                             Transform(
                                valuespec=Float(title=_("Critical at"), unit="ms"),
                                to_valuespec=lambda v: v*1000,
                                from_valuespec=lambda v: v/1000,
                             ),
                         ],
                    )),
                ],
            )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        group=RulespecGroupCheckParametersApplications,
        check_group_name="db_connection_time",
        title=lambda: _("DB Connection Time"),
        item_spec=_item_spec_db_connection_time,
        parameter_valuespec=_parameter_valuespec_db_connection_time,
        match_type="dict",
    )
)
