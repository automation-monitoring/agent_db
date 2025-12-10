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
    String,
)

def _parameter_form_mssql_version():
    return Dictionary(
            elements={
                "target_version" : DictElement(
                                parameter_form=String(title=Title("Target version")),
                                required=True,
                            ),
            },
        )


rule_spec_mssql_version = CheckParameters(
        title=Title("MSSQL Version"),
        topic=Topic.APPLICATIONS,
        name="mssql_version",
        condition=HostCondition(),
        parameter_form=_parameter_form_mssql_version,
)
