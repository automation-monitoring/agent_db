#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

import json
import re
import pprint
import traceback

from cmk.agent_based.v2 import (
    AgentSection,
    check_levels,
    CheckPlugin,
    Result,
    Service,
    State,
)


def parse_custom_sql(string_table):
    """Parse custom SQL results from agent output."""
    ret = {}
    for checkresult in string_table:
        json_content = json.loads(checkresult[0])
        if "item" not in json_content:
            # Multiple values per query are not supported yet
            continue
        item = f"{json_content['backend_service_prefix']} Custom {json_content['item']}"
        ret.update({item: json_content})
    return ret


# Register agent section
agent_section_custom_sql = AgentSection(
    name="custom_sql",
    parse_function=parse_custom_sql,
)


def _return_no_data_in_agent_output():
    return "No data in agent output, please check the statement configuration in agent_db.yml (item name, statement package, execution scope) or database permissions."


def _get_value_from_checkdata(checkdata):
    if checkdata["backend"] == "postgres":
        value = checkdata["result"][0][1][0][0]
    else:
        value = checkdata["result"][0][0][0]
    return value


def discover_custom_sql_string(section):
    for k, v in section.items():
        if v.get("type") == "string":
            yield Service(item=k)


def check_custom_sql_string(item, params, section):
    """Check custom SQL string results."""
    if item not in section:
        yield Result(state=State.UNKNOWN, summary=_return_no_data_in_agent_output())
        return

    checkdata = section[item]
    value = _get_value_from_checkdata(checkdata)

    if "\n" in value:
        summary = "Multiline output, see details"
        details = value
    else:
        summary = value
        details = None

    yield Result(state=State.OK, summary=summary, details=details)

    if params.get("expected_regex"):
        match = re.search(params["expected_regex"], value)
        yield Result(
            state=State.OK if match is not None else State.CRIT,
            notice=f'expected expression "{params["expected_regex"]}" to match',
        )


# Register check plugin for custom SQL string
check_plugin_custom_sql_string = CheckPlugin(
    name="custom_sql_string",
    sections=["custom_sql"],
    service_name="%s",
    discovery_function=discover_custom_sql_string,
    check_function=check_custom_sql_string,
    check_ruleset_name="custom_sql_string",
    check_default_parameters={},
)


def discover_custom_sql_number(section):
    for k, v in section.items():
        if v.get("type") == "number":
            yield Service(item=k)


def check_custom_sql_number(item, params, section):
    """Check custom SQL number results with levels."""
    if item not in section:
        yield Result(state=State.UNKNOWN, summary=_return_no_data_in_agent_output())
        return

    checkdata = section[item]
    pp_checkdata = pprint.pformat(checkdata)
    value = _get_value_from_checkdata(checkdata)

    if value is None:
        yield Result(
            state=State.UNKNOWN,
            summary=f"SQL return value is None. Cannot check levels.",
            details=f"Checkdata:\n{pp_checkdata}",
        )
        return

    try:
        # Define the render function based on the presence of "unit"
        if checkdata.get("unit") is not None:
            render_func = lambda v: f"{v:.2f} {checkdata['unit']}"
        else:
            render_func = lambda v: f"{v:.2f}"

        yield from check_levels(
            value,
            metric_name=checkdata.get("metric"),
            render_func=render_func,
            **params,
        )

    except Exception as e:
        # Capture the full stack trace
        error_details = traceback.format_exc()

        yield Result(
            state=State.UNKNOWN,
            summary=f"Unknown error processing '{item}' lookup check details for more information.",
            details=f"Error: {e}\n\nCheckdata:\n{pp_checkdata}\n\nError Details:\n{error_details}",
        )


# Register check plugin for custom SQL number
check_plugin_custom_sql_number = CheckPlugin(
    name="custom_sql_number",
    sections=["custom_sql"],
    service_name="%s",
    discovery_function=discover_custom_sql_number,
    check_function=check_custom_sql_number,
    check_ruleset_name="custom_sql_number",
    check_default_parameters={},
)


def discover_custom_sql(section):
    for k, v in section.items():
        if v.get("type") not in ["number", "string"]:
            yield Service(item=k)


def check_custom_sql(item, section):
    """Check custom SQL results (fallback for untyped results)."""
    if item not in section:
        yield Result(state=State.UNKNOWN, summary=_return_no_data_in_agent_output())
        return

    state = State.OK
    checkdata = section[item]
    yield Result(
        state=state,
        summary=f"Statement name: {checkdata['statement_name']}",
        details=pprint.pformat(checkdata),
    )


# Register check plugin for custom SQL (fallback)
check_plugin_custom_sql = CheckPlugin(
    name="custom_sql",
    # sections=["custom_sql"],
    # Is there another option then using the complete item as service string? Maybe do  this step better here, then in the parse function:
    # item = f"{json_content['backend_service_prefix']} Custom {json_content['item']}"
    service_name="%s",
    discovery_function=discover_custom_sql,
    check_function=check_custom_sql,
)
