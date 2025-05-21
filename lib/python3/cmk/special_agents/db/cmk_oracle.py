#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

import oracledb
import sys
import time
import re
import inspect
from cmk.special_agents.db import basedb


class DBStrategy(basedb.BaseDBStrategy):
    """Oracle DB Strategy Implementation"""

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
        self.db_host = db_host
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_cstr = db_cstr
        self.db_port = db_port
        self.db_instance = db_instance
        self.db_cursor_timeout_sec = db_cursor_timeout_sec

        self.backend = "oracle"
        self.backend_service_prefix = "ORA"
        self.sql_statement_folder = (
            f"{self.omd_root}/local/share/check_mk/agents/db/{self.backend}/sql"
        )

        self._setup_logging()
        self._initialize_oracle_client()
        # self._check_oracle_port()
        self._connect_to_oracle(db_cstr)

        self.statement_mem = {}

    def _setup_logging(self):
        current_module = inspect.getmodule(inspect.currentframe())
        self.log.name = current_module.__name__ if current_module else __name__
        self.log.debug(f"Initializing {self.backend} DB Strategy")

    def _initialize_oracle_client(self):
        """Enable thick mode to prevent PY-4011 error"""
        oracledb.init_oracle_client()

    def _check_oracle_port(self):
        """Check if the Oracle DB port is reachable."""
        check = basedb.PortChecker(
            host=self.db_host, port=self.db_port, timeout=self.db_cursor_timeout_sec
        )
        if not check.is_port_open():
            sys.stderr.write(
                f"Connection to {self.backend_service_prefix} DB failed. "
                f"Port {self.db_port}/TCP not reachable from checkmk server?\n"
            )
            sys.exit(1)

    def _connect_to_oracle(self, db_cstr):
        """Establish a connection to the Oracle DB."""
        error_message = None
        try:
            dsn = (
                db_cstr
                if db_cstr.startswith("(")
                else f"{self.db_host}:{self.db_port}/{db_cstr}"
            )
            start_connect = time.time()
            self.connection = oracledb.connect(
                user=self.db_user,
                password=self.db_pass,
                dsn=dsn,
                tcp_connect_timeout=self.db_cursor_timeout_sec,
            )
            connection_time = time.time() - start_connect
        except oracledb.DatabaseError as e:
            if "timed out" in str(error_message).lower():
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

    def _select_connection(self, state_statement_cfg, params):
        """
        Select the appropriate connection object based on the statement configuration.
        Returns the default connection, special cases should be implemented in db strategy classes.
        """
        backend, db_backend_params = params["db_backend"]
        asm_credentials = db_backend_params.get("asm_credentials")

        if state_statement_cfg.get("asm_logon", False) and asm_credentials:
            return self._get_oracle_asm_connection(asm_credentials)

        return self.connection  # Default connection

    def _get_oracle_asm_connection(self, asm_credentials):
        """Establish a connection to Oracle ASM."""
        asm_user = asm_credentials["asm_user"]
        asm_password = asm_credentials["asm_password"]

        if not hasattr(self, "asm_connection"):
            self.log.debug(
                "ASM logon enabled for statement, creating ASM connection object"
            )
            # self._check_oracle_port()

            try:
                dsn = f"{self.db_host}:{self.db_port}/+ASM"
                self.asm_connection = oracledb.connect(
                    user=asm_user,
                    password=asm_password,
                    dsn=dsn,
                    mode=oracledb.SYSDBA,
                    tcp_connect_timeout=self.db_cursor_timeout_sec,
                )
            except oracledb.DatabaseError as e:
                msg = f"Error while connecting to Oracle ASM: {e}, falling back to default connection"
                self.log.error(msg)
                sys.stderr.write(f"{msg}\n")
                self.log.debug(f"dsn: {dsn}")
                self.log.debug(f"user: {asm_user}")

        return getattr(self, "asm_connection", self.connection)

    def print_sql(self, subresult, statement_name, check_header):
        if check_header == "custom_sql":
            # Leave output as it is
            return subresult
        else:
            sql_output_string = ""
            for line in subresult:
                sql_output_string += str(line[0]) + "\n"
            return sql_output_string

    def get_version(self):
        """Get the version of the Oracle DB and return the major and minor version as a string
        Example: 213"""

        version_string = None
        try:
            statement = "SELECT * FROM v$version"
            self.cursor.execute(statement)
            ret = self.cursor.fetchone()

            self.log.debug(f"Cursor return form get_version: {ret}")

            # Regular expression pattern to match the version string
            version_pattern = r"Version (\d+\.\d+\.\d+\.\d+\.\d+)"
            release_pattern = r"Release (\d+\.\d+\.\d+\.\d+\.\d+)"

            # Iterate through the elements in the tuple
            for element in ret:
                # Use re.search to find the version string
                try:
                    version_match = re.search(version_pattern, element)
                    release_match = re.search(release_pattern, element)
                except:
                    pass
                if version_match:
                    version_string = version_match.group(1)
                    # The version string is more detailed then the release string, so we can leave the loop here
                    break
                elif release_match:
                    version_string = release_match.group(1)

            if version_string:
                version = version_string.strip("Version ").split(".")
                major_minor_version = "".join(version[:2])
                # strip major_minor_version to 3 digits
                major_minor_version_stripped = major_minor_version[:3]

                print(self.cmk_header("oracle_version_v2"))
                print(f"{self.db_cstr} {ret[0]}")
                self.log.debug(f"Original Oracle DB version string : {version_string}")
                self.log.debug(
                    f"Extracted oracle major_minor_version : {major_minor_version}"
                )
                self.log.debug(
                    f"Stripped oracle major_minor_version : {major_minor_version_stripped}"
                )
                return major_minor_version_stripped
            else:
                print("No version string found in Oracle DB return", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(
                f"Error while getting Oracle DB version from {ret}. {e}",
                file=sys.stderr,
            )
            sys.exit(1)
