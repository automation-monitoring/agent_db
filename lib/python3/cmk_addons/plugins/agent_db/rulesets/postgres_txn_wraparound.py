#!/usr/bin/env python3

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    Topic,
    HostAndItemCondition,
)
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    Dictionary,
    DictElement,
    Integer,
    LevelDirection,
    migrate_to_integer_simple_levels,
    SimpleLevels,
)


def _parameter_formspec_postgres_txn_wraparound():
    return Dictionary(
            elements={
                "unfrozen_txns" : DictElement(
                                    parameter_form=SimpleLevels(
                                        title=Title("Levels for unfrozen transactions"),
                                        level_direction=LevelDirection.UPPER,
                                        form_spec_template=Integer(),
                                        prefill_fixed_levels=DefaultValue(
                                                (1300000000, 1400000000)
                                            ),
                                        migrate=migrate_to_integer_simple_levels,
                                    ),
                                ),
                },
        )


rule_spec_postgres_txn_wraparound = CheckParameters(
        title=Title("PostgreSQL Transaction Wraparound"),
        topic=Topic.APPLICATIONS,
        name="postgres_txn_wraparound",
        condition=HostAndItemCondition(item_title=Title("DB")),
        parameter_form=_parameter_formspec_postgres_txn_wraparound,
)
