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
    LevelDirection,
    migrate_to_float_simple_levels,
    SimpleLevels,
    Percentage,
)


def _parameter_formspec_postgres_cache_hitratio():
    return Dictionary(
            elements={
                "levels_lower" : DictElement(
                                    parameter_form=SimpleLevels(
                                        title=Title("Lower levels for hitratio"),
                                        level_direction=LevelDirection.LOWER,
                                        form_spec_template=Percentage(),
                                        prefill_fixed_levels=DefaultValue((99.8, 99.5)),
                                        migrate=migrate_to_float_simple_levels,
                                    ),
                                ),
            },
        )


rule_spec_postgres_cache_hitratio = CheckParameters(
        title=Title("PostgreSQL Cache Hitratio"),
        topic=Topic.APPLICATIONS,
        name="postgres_cache_hitratio",
        condition=HostAndItemCondition(item_title=Title("DB")),
        parameter_form=_parameter_formspec_postgres_cache_hitratio,
)
