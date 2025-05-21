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
)


def _parameter_valuespec_mssql_version():
    return Dictionary(
            elements=[
                ("target_version",
                 TextInput(title=_("Target version"))),
            ],
            optional_keys=[],
        )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        group=RulespecGroupCheckParametersApplications,
        check_group_name="mssql_version",
        title=lambda: _("MSSQL Version"),
        parameter_valuespec=_parameter_valuespec_mssql_version,
        match_type="dict",
    )
)
