#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

import pymssql
import sys
import time
from datetime import datetime, timezone
import inspect
from cmk.special_agents.db import basedb


class DBStrategy(basedb.BaseDBStrategy):
    """MSSQL DB Strategy Implementation"""

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
        self.backend = "mssql"
        # used for generic custom sql check
        self.backend_service_prefix = "MSSQL"

        self.log.debug(f"Initializing {self.backend} DB Strategy")
        self.sql_statement_folder = (
            f"{self.omd_root}/local/share/check_mk/agents/db/{self.backend}/sql"
        )

        error_message = None
        connection_time = None
        self.is_first_mssql_counters_section = True
        self.mssql_tablespaces_first_line = None
        try:
            start_connect = time.time()  # Record start time
            if db_instance:
                # server_cstr = f"{db_host}\{db_instance}"
                server_cstr = f"{db_host}:{db_port}\{db_instance}"
                self.log.debug(
                    f"Instance connect to host {server_cstr} to db {db_cstr}"
                )
                self.connection = pymssql.connect(
                    user=db_user,
                    password=db_pass,
                    server=server_cstr,
                    database=db_cstr,
                    login_timeout=db_cursor_timeout_sec,
                )
            else:
                self.log.debug(
                    f"Standard connect to host {db_host} on port {db_port} to db {db_cstr}"
                )
                self.connection = pymssql.connect(
                    user=db_user,
                    password=db_pass,
                    server=db_host,
                    port=db_port,
                    database=db_cstr,
                    login_timeout=db_cursor_timeout_sec,
                )

        except pymssql.Error as e:
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
        list_dbs_query = "SELECT name FROM sys.databases"
        self.cursor.execute(list_dbs_query)
        ret = self.cursor.fetchall()
        db_list = [entry[0] for entry in ret]
        return db_list

    def get_version(self):
        # TODO: This is a placeholder, as we do not have a version query for MSSQL yet
        # 15 was only a dummy value for testing
        return "15.0"

    def _add_database_in_front(self, ret):
        mod_ret = []
        for ret_tuple in ret:
            mod_ret.append((self.db_cstr,) + ret_tuple)
            # mod_ret.append()
        return mod_ret

    def _add_def_prefix(self, ret):
        mod_ret = []
        for ret_tuple in ret:
            mod_ret.append(("DB",) + ret_tuple)
        return mod_ret

    def transform_subresult(self, statement_name, subresult):
        if statement_name == "mssql_transactionlogs":
            subresult = self._add_database_in_front(subresult)
            subresult = self._add_def_prefix(subresult)
        elif statement_name == "mssql_datafiles":
            subresult = self._add_database_in_front(subresult)
            subresult = self._add_def_prefix(subresult)
        elif statement_name == "mssql_availability_groups":
            pass
            # subresult = self._add_database_in_front(subresult)
        elif statement_name == "mssql_counters":
            # NOTE: We only have one entry per line here, as concatenation is done in the SQL statement
            #       This is why we use map to split at the |
            # TODO: Remove concatenation from SQL file and splitting here
            subresult = [
                (
                    e[0].replace("$", "_").replace(" ", "_"),
                    e[1].lower().replace(" ", "_"),
                    e[2].replace(" ", "_")
                    if e[2] != ""
                    else "None",  # Yes, mssql.vbs does this m(
                    e[3],
                )
                for e in map(lambda x: x[0].split("|"), subresult)
            ]
            if self.is_first_mssql_counters_section:
                subresult = [
                    (
                        "None",
                        "utc_time",
                        "None",
                        datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M:%S"),
                    )
                ] + subresult
                self.is_first_mssql_counters_section = False
        elif statement_name == "mssql_tablespaces":
            # TODO: This looks horrible because we need to access multiple lines,
            #       which this function does not anticipate. We leave it here for now,
            #       where all the bending-the-result-to-the-original-plugin happens.
            #       A future additional layer for transforming the entire section should
            #       be introduced and this variable kicked out.
            # NOTE: In the original plugin, the DB instance is prefixed in the place where
            #       we add the default prefix here. This is fine (for now) in our case,
            #       as in contrast to Checkmk's mssql.vbs, we do not query local databases
            #       on a system (where multiple instances are common), but listeners as
            #       an application would, which only ever reference one instance.
            #       Should a future use case turn up where multiple instances are monitored
            #       with this special agent, the default prefix is what needs to be replaced.
            if self.mssql_tablespaces_first_line is None:
                self.mssql_tablespaces_first_line = subresult[0]
                subresult = []
            else:
                subresult = [self.mssql_tablespaces_first_line + subresult[0]]
                subresult = self._add_def_prefix(subresult)
                self.mssql_tablespaces_first_line = None
        elif statement_name == "mssql_backup":
            # NOTE: We need to add +00:00 to the timezone, otherwise the builtin check
            #       will not interpret the timestamp as UTC but according to local time
            transform_line = lambda s: (s[0],) + tuple((s[1]+"+00:00").split()) + (s[6],)
            subresult = list(map(transform_line, subresult))
            subresult = self._add_def_prefix(subresult)
        elif statement_name == "mssql_databases":
            transform_line = lambda s: (
                s[0],
                s[1].decode("utf-8"),
                s[2].decode("utf-8"),
                # TODO: Replace with CAST(value AS INT) AS value in SQL? Test and simplify if possible
                int.from_bytes(s[3], byteorder="little"),
                int.from_bytes(s[4], byteorder="little"),
            )
            subresult = list(map(transform_line, subresult))
            subresult = self._add_def_prefix(subresult)
        elif statement_name == "mssql_jobs":
            replace_none = lambda v: "" if v is None else v
            transform_line = lambda l: tuple(map(replace_none, l))
            subresult = list(map(transform_line, subresult))
        else:
            subresult = self._add_def_prefix(subresult)
        return subresult

    def transform_result(self, statement_name, check_header, result):
        if statement_name == "mssql_blocked_sessions":
            if len(result) == 1 and len(result[0]) == 0:
                result = [[("No blocking sessions",)]]
        yield from super().transform_result(statement_name, check_header, result)

    def print_sql(self, subresult, statement_name, check_header):
        if check_header == "custom_sql":
            # Leave output as it is
            return subresult
        else:
            sql_output_string = ""
            for line in subresult:
                sql_output_string += (
                    self.separator_char.join([str(val).strip() for val in line]) + "\n"
                )
            return sql_output_string

    @staticmethod
    def query(cursor, sqlstatement):
        if sqlstatement.startswith("BEGIN") or sqlstatement.startswith("DECLARE"):
            sqls = [sqlstatement]
        else:
            sqls = sqlstatement.split(";")

        for sql in sqls:
            cursor.execute(sql)
            while True:
                ret = cursor.fetchall()
                yield ret
                if not cursor.nextset():
                    break
