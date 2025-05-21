#!/usr/bin/env python3

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)

from cmk.gui.valuespec import (
    Dictionary,
    Tuple,
    Percentage,
    TextInput,
)


def _item_spec_postgres_cache_hitratio():
    return TextInput(title=_("DB"))


def _parameter_valuespec_postgres_cache_hitratio():
    return Dictionary(
            elements=[
                ("levels_lower",
                    Tuple(
                        title=_("Lower levels for hitratio"),
                        elements=[
                            Percentage(title=_("Warning below")),
                            Percentage(title=_("Critical below")),
                        ],
                    )
                ),
            ],
        )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        group=RulespecGroupCheckParametersApplications,
        check_group_name="postgres_cache_hitratio",
        title=lambda: _("PostgreSQL Cache Hitratio"),
        item_spec=_item_spec_postgres_cache_hitratio,
        parameter_valuespec=_parameter_valuespec_postgres_cache_hitratio,
        match_type="dict",
    )
)
