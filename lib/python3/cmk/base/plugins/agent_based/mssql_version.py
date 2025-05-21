#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
from .agent_based_api.v1 import Result, State, Service, register

MSSQL_VERSION_MAPPING = {
    "8": "2000",
    "9": "2005",
    "10": "2008",
    "10.50": "2008R2",
    "11": "2012",
    "12": "2014",
    "13": "2016",
    "14": "2017",
    "15": "2019",
    "16": "2022",
}


def _parse_prod_version(entry):
    major_version, minor_version = entry.split(".", 2)[:2]
    if not (
        version := MSSQL_VERSION_MAPPING.get(
            f"{major_version}.{minor_version}",
            MSSQL_VERSION_MAPPING.get(major_version),
        )
    ):
        return f"unknown[{entry}]"
    return f"Microsoft SQL Server {version}"


def _clean_bytestring_repr(s):
    if s.startswith("b'") and s.endswith("'"):
        return s[2:-1]
    return s


def discover_mssql_version(section):
    yield Service()


def check_mssql_version(params, section):
    version_number = _clean_bytestring_repr(section[0][1])
    edition = _clean_bytestring_repr(section[0][3])
    version_name = _parse_prod_version(version_number)
    summary = f"{version_name} {edition} ({version_number})"
    if params.get("target_version") is not None:
        target_version = params["target_version"]
        if version_number != target_version:
            summary += f" (expected version {target_version})"
            yield Result(state=State.WARN, summary=summary)
        else:
            yield Result(state=State.OK, summary=summary)
    else:
        yield Result(state=State.OK, summary=summary)


register.check_plugin(
    name="mssql_version",
    service_name="MSSQL Version",
    discovery_function=discover_mssql_version,
    check_function=check_mssql_version,
    check_default_parameters={},
    check_ruleset_name="mssql_version",
)
