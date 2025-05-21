#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

from .agent_based_api.v1 import Result, State, Service, Metric, register
import json
import pprint

defaults_db_connection_time = {"db_cursor_avail_sec": (1.5, 3.0)}


# representation of time in human readable format (input seconds)
def _human_readable_time(seconds):
    if seconds < 1:
        return "%.2f ms" % (seconds * 1000)
    elif seconds < 60:
        return "%.2f sec" % seconds
    elif seconds < 3600:
        return "%.2f min" % (seconds / 60)
    else:
        return "%.2f h" % (seconds / 3600)


def parse_db_connection_time(string_table):
    # example data:
    #    [['{"db_cstr":',
    #  '"projdat",',
    #  '"connection_time":',
    #  '0.008624076843261719,',
    #  '"error":',
    #  'null}'],
    # ['{"db_cstr":',
    #  '"master",',
    #  '"connection_time":',
    #  '0.006785392761230469,',
    #  '"error":',
    #  'null}']]

    ret = {}
    for line in string_table:
        try:
            # Join the fragmented JSON string
            json_string = " ".join(line)
            # Parse the JSON string
            loaded_data = json.loads(json_string)

            # Extract the relevant information from the JSON
            db_name = loaded_data["db_cstr"]
            connection_time = loaded_data["connection_time"]
            error = loaded_data["error"]

            # Store the data in the result dictionary
            ret[db_name] = {"connection_time": connection_time, "error": error}
        except json.JSONDecodeError as e:
            # Handle the JSON decoding error
            print(f"Error decoding JSON: {e}")
        except KeyError as e:
            # Handle missing keys in the parsed data
            print(f"Missing key in the parsed data: {e}")

    return ret


register.agent_section(
    name="mysql_connection_time",
    parse_function=parse_db_connection_time,
)
register.agent_section(
    name="oracle_connection_time",
    parse_function=parse_db_connection_time,
)
register.agent_section(
    name="mssql_connection_time",
    parse_function=parse_db_connection_time,
)
register.agent_section(
    name="postgres_connection_time",
    parse_function=parse_db_connection_time,
)


def discover_db_connection_time(section):
    for db_cstr in section.keys():
        yield Service(item=db_cstr)


def check_db_connection_time(item, params, section):
    try:
        connection_time = float(section[item]["connection_time"])
        error = section[item]["error"]
        warn, crit = params["db_cursor_avail_sec"]
        if error:
            yield Result(
                state=State.CRIT,
                summary=f"Unable to connect to Database {item}",
                details=str(error),
            )
            return
        elif connection_time >= crit:
            state = State.CRIT
        elif connection_time >= warn:
            state = State.WARN
        else:
            state = State.OK
        yield Metric(name="db_connect_time", value=connection_time, levels=(warn, crit))
        yield Result(
            state=state,
            summary="Connection to database established within %s"
            % _human_readable_time(connection_time),
        )

    except KeyError as e:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Unable to calculate connection time for database {str(e)}, no data in agent output",
            details=f"Database not found in {section}",
        )

    except Exception as e:
        yield Result(
            state=State.UNKNOWN,
            summary="Unable to parse connection time",
            details=str(e),
        )


register.check_plugin(
    name="mssql_connection_time",
    sections=["mssql_connection_time"],
    service_name="MSSQL DB Connect %s",
    discovery_function=discover_db_connection_time,
    check_function=check_db_connection_time,
    check_default_parameters=defaults_db_connection_time,
    check_ruleset_name="db_connection_time",
)

register.check_plugin(
    name="mysql_connection_time",
    sections=["mysql_connection_time"],
    service_name="MySQL DB Connect %s",
    discovery_function=discover_db_connection_time,
    check_function=check_db_connection_time,
    check_default_parameters=defaults_db_connection_time,
    check_ruleset_name="db_connection_time",
)

register.check_plugin(
    name="oracle_connection_time",
    sections=["oracle_connection_time"],
    service_name="ORA DB Connect %s",
    discovery_function=discover_db_connection_time,
    check_function=check_db_connection_time,
    check_default_parameters=defaults_db_connection_time,
    check_ruleset_name="db_connection_time",
)

register.check_plugin(
    name="postgres_connection_time",
    sections=["postgres_connection_time"],
    service_name="PostgreSQL DB Connect %s",
    discovery_function=discover_db_connection_time,
    check_function=check_db_connection_time,
    check_default_parameters=defaults_db_connection_time,
    check_ruleset_name="db_connection_time",
)
