#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

import psycopg2
import sys
import time
import inspect
from cmk.special_agents.db import basedb

_sections_with_db_list = [
    "postgres_bloat",
    "postgres_query_duration",
    "postgres_locks",
    "postgres_connections",
    "postgres_stats",
]

_sections_without_column_names = [
    "postgres_sessions",
    "postgres_version",
]


class DBStrategy(basedb.BaseDBStrategy):
    """MySQL DB Strategy Implementation"""

    def __init__(
        self,
        db_host,
        db_hostname,
        db_user,
        db_pass,
        db_cstr,
        db_port,
        db_instance,
        db_cursor_timeout_sec,
        loglevel,
    ):
        super().__init__(
            db_host,
            db_hostname,
            db_user,
            db_pass,
            db_cstr,
            db_port,
            db_instance,
            db_cursor_timeout_sec,
            loglevel,
        )
        # Get the name of the current strategy module
        current_module = inspect.getmodule(inspect.currentframe())
        self.log.name = current_module.__name__ if current_module else __name__

        self.backend = "postgres"
        # used for generic custom sql check
        self.backend_service_prefix = "PostgreSQL"

        self.log.debug(f"Initializing {self.backend} DB Strategy")
        self.sql_statement_folder = (
            f"{self.omd_root}/local/share/check_mk/agents/db/{self.backend}/sql"
        )

        # TODO: Discuss this more deeply with someone who knows Postgres really well
        self.db_instance = db_instance if db_instance is not None else "main"

        error_message = None
        connection_time = None
        try:
            start_connect = time.time()  # Record start time
            self.connection = psycopg2.connect(
                host=db_host,
                port=db_port,
                dbname=db_cstr,
                user=db_user,
                password=db_pass,
                connect_timeout=db_cursor_timeout_sec,
            )
        except psycopg2.Error as e:
            if "timed out" in str(e).lower():
                error_message = self.format_error_message(db_cstr, e, timeout=True)
            else:
                error_message = self.format_error_message(db_cstr, e)

        if error_message:
            self.log.error(error_message)
            self.print_backend_connection_time(self.backend, db_cstr, 0, error_message)
            # set connection to FormattedErrorMessage to prevent further usage
            self.connection = error_message

        else:
            self.cursor = self.connection.cursor()
            cursor_created = time.time()  # Record end time after cursor is created
            connection_time = (
                cursor_created - start_connect
            )  # Calculate connection time
            self.print_backend_connection_time(self.backend, db_cstr, connection_time)

    def list_all_dbs(self):
        list_dbs_query = "SELECT datname FROM pg_database WHERE datistemplate = false;"
        self.cursor.execute(list_dbs_query)
        ret = self.cursor.fetchall()
        db_list = [entry[0] for entry in ret]
        return db_list

    def get_version(self):
        # get version from postgres
        statement = "SELECT version()"
        self.cursor.execute(statement)
        ret = self.cursor.fetchone()
        self.log.debug(f"Version returned: {ret}")
        # Example: ret = 'PostgreSQL 16.2 (Debian 16.2-1.pgdg120+2) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit'
        version = ret[0].split()[1]
        self.log.debug(f"Version parsed: {version}")
        return version

    def transform_subresult(self, statement_name, subresult):
        if statement_name == "postgres_sessions":
            replace_boolean = lambda r: ("t", r[1]) if r[0] is True else ("f", r[1]) if r[0] is False else r
            subresult = list(map(replace_boolean, subresult))
        elif statement_name == "postgres_bloat":
            # The postgres_bloat query returns one subresult that is only the
            # title line, and then a subresult with multiple lines.
            for idx, line in enumerate(subresult):
                if line[0] == "db" and line[1] == "schemaname":
                    continue
                # Checkmk expects integers here. These should always be
                # integer-equal floats.
                wastedibytes = float(subresult[idx][16])
                try:
                    assert int(wastedibytes) == wastedibytes
                # If these for some reason are *not* integer-equal floats,
                # we want to know about it without crashing the entire agent.
                # This will crash the postgres_bloat check.
                except AssertionError:
                    return subresult
                subresult[idx] = (
                    subresult[idx][:16]
                    + ("%d" % int(wastedibytes),)
                    + subresult[idx][17:]
                )
        return subresult

    def transform_result(self, statement_name, check_header, result):
        if check_header == "custom_sql":
            yield result

        else:
            yield [(f"[[[{self.db_instance}]]]",)]
            if statement_name in _sections_with_db_list:
                yield [("[databases_start]",)]
                yield [(self.db_cstr,)]
                yield [("[databases_end]",)]
            if statement_name in _sections_without_column_names:
                start_line = 1
            else:
                start_line = 0

            # Apparently, this missing line can lead to empty sections in some cases,
            # see also comment in original mk_postgres plugin
            if statement_name == "postgres_sessions":
                true_in_sr = lambda sr: True if True in [e[0] for e in sr] else False
                if len([sr for sr in result if true_in_sr(sr)]) == 0:
                    result.append([(True, 0)])

            for subresult in result[start_line:]:
                yield self.transform_subresult(statement_name, subresult)

    @staticmethod
    def sanitize_output(out_str):
        # Outputs can contain newlines, which will be parsed
        # incorrectly by the original Checkmk postgres checks.
        # Checkmk's mk_postgres replaces unicode newline chars
        # with spaces.
        sanitized = out_str.replace("\n", " ")
        return sanitized

    def print_sql(self, subresult, statement_name, check_header):
        if check_header == "custom_sql":
            # Leave output as it is
            return subresult
        else:
            sql_output_string = ""
            for line in subresult:
                line_strings = [
                    self.sanitize_output(str(val)) if val is not None else ""
                    for val in line
                ]
                sql_output_string += self.separator_char.join(line_strings)
                sql_output_string += "\n"

            return sql_output_string

    @staticmethod
    def query(cursor, sqlstatement):
        """
        Run an SQL statement with an open cursor.
        """
        if sqlstatement.startswith("BEGIN"):
            sqls = [sqlstatement]
        else:
            sqls = sqlstatement.split(";")

        for sql in sqls:
            cursor.execute(sql)
            # Checkmk's Postgres checks reference a title row. This is
            # not returned as part of the query's response, but rather as
            # metadata in the cursor object.
            yield [tuple([desc[0] for desc in cursor.description])]
            ret = cursor.fetchall()
            yield ret
