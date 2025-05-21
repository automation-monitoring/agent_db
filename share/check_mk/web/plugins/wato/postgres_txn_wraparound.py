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
    Transform,
    Integer,
    TextInput,
)


def _item_spec_postgres_txn_wraparound():
    return TextInput(title=_("DB"))


def _parameter_valuespec_postgres_txn_wraparound():
    return Dictionary(
            elements=[
                ("unfrozen_txns",
                    Tuple(
                        title=_("Levels for unfrozen transactions"),
                        elements=[
                            Integer(title=_("Warning at"), default_value=1300000000),
                            Integer(title=_("Critical at"), default_value=1400000000),
                        ],
                    )
                ),
            ],
        )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        group=RulespecGroupCheckParametersApplications,
        check_group_name="postgres_txn_wraparound",
        title=lambda: _("PostgreSQL Transaction Wraparound"),
        item_spec=_item_spec_postgres_txn_wraparound,
        parameter_valuespec=_parameter_valuespec_postgres_txn_wraparound,
        match_type="dict",
    )
)
