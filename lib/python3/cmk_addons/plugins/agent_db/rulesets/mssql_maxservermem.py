#!/usr/bin/env python3

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    Topic,
    HostCondition,
)
from cmk.rulesets.v1.form_specs import (
    Dictionary,
    DictElement,
    Integer,
)


def _parameter_form_mssql_version():
    return Dictionary(
            elements={
                "maxservermem" : DictElement(
                        parameter_form=Integer(title=Title("Server Memory in MB")),
                        required=True,
                    ),
            },
        )


rule_spec_mssql_maxservermem = CheckParameters(
        title=Title("MSSQL Max Server Memory"),
        topic=Topic.APPLICATIONS,
        name="mssql_maxservermem",
        condition=HostCondition(),
        parameter_form=_parameter_form_mssql_version,
)
