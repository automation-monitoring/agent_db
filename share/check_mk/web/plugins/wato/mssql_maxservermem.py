#!/usr/bin/env python3

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithoutItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)

from cmk.gui.valuespec import (
    Dictionary,
    TextInput,
    Integer,
)


def _parameter_valuespec_mssql_version():
    return Dictionary(
            elements=[
                ("maxservermem",
                 Integer(title=_("Server Memory in MB"))),
            ],
            optional_keys=[],
        )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        group=RulespecGroupCheckParametersApplications,
        check_group_name="mssql_maxservermem",
        title=lambda: _("MSSQL Max Server Memory"),
        parameter_valuespec=_parameter_valuespec_mssql_version,
        match_type="dict",
    )
)
