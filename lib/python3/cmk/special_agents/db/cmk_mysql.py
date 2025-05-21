#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

import mysql.connector
import sys
import time
import inspect
from cmk.special_agents.db import basedb


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

        self.backend = "mysql"
        # used for generic custom sql check
        self.backend_service_prefix = "MySQL"

        self.log.debug(f"Initializing {self.backend} DB Strategy")
        self.sql_statement_folder = (
            f"{self.omd_root}/local/share/check_mk/agents/db/{self.backend}/sql"
        )

        error_message = None
        connection_time = None
        try:
            start_connect = time.time()  # Record start time
            self.connection = mysql.connector.connect(
                user=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
                database=db_cstr,
                connection_timeout=db_cursor_timeout_sec,
            )
        except mysql.connector.Error as e:
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

    def get_version(self):
        # get version from mysql
        statement = "SELECT version()"
        self.cursor.execute(statement)
        ret = self.cursor.fetchone()
        # Example: ret = 10.3.38-MariaDB-0ubuntu0.20.04.1
        version = ret[0].split("-")[0]
        version = version.split(".")
        major_minor_version = "".join(version[:2])
        return major_minor_version
        # return "8.0.26"

    def print_sql(self, subresult, statement_name, check_header):
        if check_header == "custom_sql":
            # Leave output as it is
            return subresult
        else:
            subresult_string = ""
            for line in subresult:
                for val in line:
                    subresult_string += str(val) + " "
                subresult_string += "\n"
            return subresult_string
