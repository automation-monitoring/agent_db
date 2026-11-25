#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

import json
import base64
from copy import deepcopy

from cmk.server_side_calls.v1 import (
    SpecialAgentCommand,
    SpecialAgentConfig,
    noop_parser,
)


def _resolve_custom_host_attr(value, macros):
    """Resolve "<<attr>>" from the host macros.

    Checkmk provides a custom host attribute as macro $_HOST<attr>$ if the
    attribute has "Add to monitoring configuration" enabled. Unresolved
    values are returned unchanged, so the agent can still fall back to the
    REST API.
    """
    if not (isinstance(value, str) and value.startswith("<<") and value.endswith(">>")):
        return value
    name = value[2:-2]
    for key in (f"$_HOST{name}$", f"$_HOST{name.upper()}$"):
        if key in macros:
            return macros[key]
    return value


def resolve_custom_host_attrs(params, macros):
    """Resolve "<<attr>>" values in the rule and backend parameters.

    Same semantics as the agent: for db_cstr (a list) only the first
    element is looked at and the whole list is replaced by the attribute
    value (the agent splits it at ";").
    """
    for section in (params, params["db_backend"][1]):
        for key, value in section.items():
            if key == "db_cstr" and isinstance(value, list) and value:
                resolved = _resolve_custom_host_attr(value[0], macros)
                if resolved != value[0]:
                    section[key] = resolved
            else:
                section[key] = _resolve_custom_host_attr(value, macros)


def generate_agent_db_commands(params, host_config):
    password_arg = params["password"]

    # Build dict to later dump to b64. We need to deepcopy here,
    # because modifying params leads to errors when this function
    # is called multiple times in the same process passing the same
    # params object. This happens in regular checkmk operation
    params_b64 = deepcopy(params)

    # Do not include passwords in the b64 argument for security
    params_b64 = {k:v for k,v in params_b64.items() if k != "password"}

    asm_pw = None
    if params_b64["db_backend"][0] == "cmk_oracle":
        oracle_params = params_b64["db_backend"][1]
        if "asm_credentials" in oracle_params:
            asm_pw = oracle_params["asm_credentials"]["asm_password"]
            del oracle_params["asm_credentials"]["asm_password"]

    resolve_custom_host_attrs(params_b64, host_config.macros)

    # Dump params to JSON and serialize to a base64 string
    json_params = json.dumps(params_b64)
    base64_params = base64.b64encode(json_params.encode()).decode()

    args = [
        "--base64args",
        base64_params,
        "--hostname",
        host_config.name,
        "--ipaddress",
        host_config.ipv4_config.address,
        "--password",
        password_arg,
    ]
    if asm_pw is not None:
        args += ["--asm_password", asm_pw]
    yield SpecialAgentCommand(command_arguments=args)


special_agent_db = SpecialAgentConfig(
    name="db",
    parameter_parser=noop_parser,
    commands_function=generate_agent_db_commands,
)
