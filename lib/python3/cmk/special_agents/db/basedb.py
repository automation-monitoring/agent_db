#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

import os
import sys
import json
import time
import threading
import socket

from cmk.special_agents import agent_db
from cmk.special_agents.db import cache


class BaseDBStrategy(agent_db.AgentDBLog):
    """Base DB Strategy Implementation"""

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
        self.omd_root = os.environ["OMD_ROOT"]
        super().__init__(f"{self.omd_root}/var/log/agent_db/{db_host}.log", loglevel)

        self.omd_tmp = self.omd_root + "/var/tmp/agent_db"
        # Create the tmp directory if it does not exist
        if not os.path.exists(self.omd_tmp):
            os.makedirs(self.omd_tmp)
        self.cache_dir = self.omd_tmp + "/cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        self.sql_statement_folder = None  # To be set in subclass
        self.db_host = db_host
        self.db_hostname = db_hostname
        self.db_port = db_port
        self.db_cstr = db_cstr
        self.db_cursor_timeout_sec = db_cursor_timeout_sec
        self.log.debug("Initializing Base DB Strategy")

        # Populated by query() with the column names (from cursor.description)
        # of the last executed statement, one tuple per executed SQL part.
        # Used to resolve item_columns/value_column when they are given as
        # column names instead of numeric indices. Postgres does not use this
        # (its query() already yields the header row as part of the result).
        self.last_column_names = None

        # Initialize the database connection
        # self.init_db_connection(db_host, db_user, db_pass, db_cstr, db_port)

    class FormattedErrorMessage:
        def __init__(self, message):
            self.message = message

        def __repr__(self):
            return self.message

        def __str__(self):
            return self.message

    def list_all_dbs(self):
        raise NotImplementedError("Not implemented for this backend")

    def close_db_connection(self):
        if self.connection is not None:
            self.connection.close()

    def create_db_connection(self, db_host, db_user, db_pass, db_cstr, db_port):
        # To be implemented in subclass
        pass

    def get_db_type(self):
        # To be implemented in subclass
        pass

    def get_version(self):
        # To be implemented in subclass
        pass

    @staticmethod
    def is_version_string(mystery_string):
        return all(c in ".0123456789" for c in mystery_string)

    @staticmethod
    def comparable_version_from_string(version_string):
        """
        Turn a version string into an object we can sort and compare

        This only works for version strings like 1.0.4 or 304
        but not for c1.23.4r5 or 1.3.0p24
        """
        return tuple([int(ver) for ver in version_string.split(".")])

    def transform_subresult(self, statement_name, subresult):
        # To be implemented in subclass
        return subresult

    def transform_result(self, statement_name, check_header, result):
        for subresult in result:
            if check_header == "custom_sql":
                yield subresult
            else:
                yield self.transform_subresult(statement_name, subresult)

    def print_sql(self, parsed_sql):
        # To be implemented in subclass
        pass

    def output_statement_result(self, statement_name, check_header, result):
        for subresult in self.transform_result(statement_name, check_header, result):
            yield (self.print_sql(subresult, statement_name, check_header))
            # sys.stdout.write(self.print_sql(subresult))

    def cmk_header(
        self, header, separator=None, check_timestamp=None, cache_time_sec=None
    ):
        # <<<oracle_rman:sep(124):cached(1708501707,1200)>>>
        cmk_header = f"<<<{header}"
        if separator is not None:
            cmk_header += f":{separator}"
        if check_timestamp is not None and cache_time_sec is not None:
            cmk_header += f":cached({check_timestamp},{cache_time_sec})"
        cmk_header += ">>>"
        return cmk_header

    def find_suitable_version(self, sql_version_numbers, db_version):
        # Find out the closest version number
        # Example list: version_numbers = [121, 92]

        # If there is a version number in the list of sql_version_numbers which is smaller than the db_version number then use this one.
        # In case that there are more then one version is smaller than the db_version number then use the highest one.
        # Example: db_version = 190, sql_version_numbers = [121, 92] --> closest_version = 121
        # Filter version numbers to those smaller than db_version
        versions_smaller_than_db = [
            version_number
            for version_number in sql_version_numbers
            if version_number <= self.comparable_version_from_string(db_version)
        ]

        if versions_smaller_than_db:
            closest_version = max(versions_smaller_than_db)
            return closest_version
        else:
            return None

    def read_statement(self, statement, db_version):
        # Example Versions 92, 102, 121, 180, 213
        # Read SQL statement from file and return statement
        # If there are no statement files with a version number, use the statement without a version number
        # elif there is a file with the exact suffix _<version> then use this one.
        # else use the number which is closest to the version number

        self.log.debug(f"Reading statement {statement} for version {db_version}")

        # Get the list of files in the statement folder
        statement_files = os.listdir(self.sql_statement_folder)

        # Filter the files based on the statement and version
        filtered_files = [
            filename
            for filename in statement_files
            if filename.startswith(f"{statement}_")
            and self.is_version_string(filename.rsplit("_", 1)[1][:-4])
        ]
        sql_version_numbers = [
            self.comparable_version_from_string(filename.rsplit("_", 1)[1][:-4])
            for filename in filtered_files
        ]

        closest_version = self.find_suitable_version(sql_version_numbers, db_version)

        if closest_version is not None:
            closest_version_string = ".".join(map(str, closest_version))
            statement_file = (
                f"{self.sql_statement_folder}/{statement}_{closest_version_string}.sql"
            )
        else:
            self.log.debug(
                f"No explicit version found for statement {statement} and version {db_version}"
            )
            # Try to fallback to the statement without a version number if file exists
            statement_file = f"{self.sql_statement_folder}/{statement}.sql"
            if not os.path.exists(statement_file):
                self.log.error(
                    f"No fallback statement file without version number found"
                )
                return None

        self.log.debug(f"Reading statement {statement} from {statement_file}")
        # Read the statement from the selected file
        with open(statement_file, "r") as sqlfile:
            sql_statement = sqlfile.read()

        # Remove trailing newline and semicolon from the statement
        sql_statement = sql_statement.rstrip("\n").rstrip(";")
        return sql_statement

    def extract_packages_from_backend_params(self, backend_params):
        """
        Extract the packages from the backend parameters.

        Args:
            backend_params (dict): Backend parameters.

        Returns:
            list: List of packages extracted from the backend parameters.
        """
        packages = []
        for key in backend_params:
            # If key ends with "_pkgs" then it should be package list
            # To ensure that keep that in mind while defining the backend parameters in wato
            if key.endswith("_pkgs"):
                packages.extend(backend_params[key])

        return packages

    def exec_statements(self, statement_cfg, backend_params, params):
        """
        Execute the statements from the statement_cfg.

        Args:
            statement_cfg (dict): Configuration for the statements to be executed.
            backend_params (dict): Backend parameters.

        Returns:
            None
        """
        if not "statement_desc" in statement_cfg:
            self.log_error_and_exit(
                "No statement description found in agent configuration!"
            )

        db_version = self.get_version()

        for statement_name, state_statement_cfg in statement_cfg[
            "statement_desc"
        ].items():
            if self._is_statement_matching(state_statement_cfg, backend_params):
                self.log.debug(f"Select connection for statement: {statement_name}")
                connection = self._select_connection(state_statement_cfg, params)

                execution_scope = state_statement_cfg.get("execution_scope")
                # Flags for checking execution scope criteria
                connection_string_match = True
                db_hostname_match = True

                # If execution_scope is defined, check individual conditions
                if execution_scope:
                    # Check if the current database connection string is in the execution scope, if defined
                    if "connection_string" in execution_scope:
                        connection_string_match = (
                            self.db_cstr in execution_scope["connection_string"]
                        )

                    # Check if the current database hostname is in the execution scope, if defined
                    if "db_hostname" in execution_scope:
                        db_hostname_match = (
                            self.db_hostname in execution_scope["db_hostname"]
                        )

                # Execute statement if both conditions (if defined) are met
                if connection_string_match and db_hostname_match:
                    self._execute_statement(
                        statement_name,
                        state_statement_cfg,
                        connection,
                        db_version,
                        statement_cfg,
                    )
                else:
                    self.log.debug(f"Statement {statement_name} not in execution scope")

    def _is_statement_matching(self, state_statement_cfg, backend_params):
        """
        Determine if the statement matches the backend parameters.

        Args:
            state_statement_cfg (dict): Configuration of the current statement.
            backend_params (dict): Backend parameters.

        Returns:
            bool: True if the statement matches, False otherwise.
        """
        for pkg in self.extract_packages_from_backend_params(backend_params):
            if pkg in state_statement_cfg["packages"]:
                return True
        return False

    def _select_connection(self, state_statement_cfg, params):
        """
        Select the appropriate connection object based on the statement configuration.
        Returns the default connection, special cases should be implemented in db strategy classes.

        Args:
            state_statement_cfg (dict): Configuration of the current statement.

        Returns:
            Connection object to be used for executing the statement.
        """
        return self.connection  # Default connection

    def _execute_statement(
        self, statement_name, state_statement_cfg, connection, db_version, statement_cfg
    ):
        """
        Execute a single statement using the provided connection.

        Args:
            statement_name (str): The name of the statement.
            state_statement_cfg (dict): Configuration of the current statement.
            connection: The connection object to use for executing the statement.
            db_version (str): The version of the database.
            statement_cfg (dict): Configuration for all statements.

        Returns:
            None
        """
        self.separator = state_statement_cfg.get(
            "separator", statement_cfg.get("default_separator")
        )
        sqlstatement_timeout = state_statement_cfg.get(
            "timeout_sec", statement_cfg.get("default_timeout_sec", 15)
        )
        cache_time_sec = cache.get_cache_time_in_seconds(state_statement_cfg)

        self.log.debug(f"Statement: {statement_name}, cache_time_sec: {cache_time_sec}")

        check_header = state_statement_cfg.get("check_header", statement_name)
        sql_statement = self.read_statement(statement_name, db_version)

        if sql_statement is None:
            self.log.error(
                f"Skipping execution of statement {statement_name} due to missing statement file"
            )
            return

        result, mtime_cache_file = self.exec_sql(
            connection,
            statement_name,
            sql_statement,
            sqlstatement_timeout,
            cache_time_sec,
        )

        self._output_result(
            check_header, result, state_statement_cfg, mtime_cache_file, cache_time_sec
        )

    def _output_result(
        self,
        check_header,
        result,
        state_statement_cfg,
        mtime_cache_file,
        cache_time_sec,
    ):
        """
        Output the result of the executed statement.

        Args:
            check_header (str): The header for the output.
            result: The result of the SQL execution.
            state_statement_cfg (dict): Configuration of the current statement.
            mtime_cache_file: Modification time of the cache file.
            cache_time_sec: Cache time in seconds.

        Returns:
            None
        """
        sys.stdout.write(
            self.cmk_header(
                check_header, self.separator, mtime_cache_file, cache_time_sec
            )
            + "\n"
        )

        checkoutput = {"result": ""}

        if check_header == "custom_sql":
            result_list = list(
                self.output_statement_result(check_header, check_header, result)
            )

            if "item_columns" in state_statement_cfg and "value_column" in state_statement_cfg:
                # Multiline mode: the statement is allowed to return more than
                # one row. Each row becomes its own checkmk service/item.
                self._output_custom_sql_multiline(
                    check_header, result_list, state_statement_cfg
                )
            else:
                # Legacy/default mode: only the first row of the result is used
                # and the item name comes statically from state_statement_cfg["item"].
                checkoutput.update({"backend": self.backend})
                checkoutput.update(
                    {"backend_service_prefix": self.backend_service_prefix}
                )
                checkoutput.update({"db_cstr": self.db_cstr})
                checkoutput.update({"statement_name": check_header})

                checkoutput["result"] = result_list
                checkoutput.update(state_statement_cfg)
                sys.stdout.write(json.dumps(checkoutput) + "\n")
        else:
            for line in self.output_statement_result(
                check_header, check_header, result
            ):
                checkoutput["result"] += line

            sys.stdout.write(checkoutput["result"])

    def _extract_custom_sql_data_rows(self, result_list):
        """
        Normalize the nested result structure of a custom_sql statement into a
        plain list of data rows (tuples), regardless of the DB backend.

        Background: for "custom_sql", output_statement_result() (via
        transform_result()/print_sql()) behaves differently per backend:
          - postgres: transform_result() yields the *entire* nested result
            exactly once (`yield result`), so result_list has ONE outer
            element, which itself is [ [(<col1>, <col2>, ...)], [(row1_col1,
            ...), ...] ] -- i.e. the column header tuple, then the data rows:
            result_list = [ [ [(<col1>, ...)], [(row1_col1, ...), ...] ] ]
          - all other backends: transform_result() yields each subresult of
            `result` separately, and for a single (non ";"-separated)
            statement there is exactly one subresult -- the data rows -- so:
            result_list = [ [(row1_col1, row1_col2, ...), ...] ]

        Args:
            result_list (list): The value produced by
                list(self.output_statement_result(...)) for a custom_sql
                statement.

        Returns:
            list: A flat list of row tuples, e.g. [(row1_col1, ...), (row2_col1, ...)]
        """
        if self.backend == "postgres":
            if not result_list or len(result_list[0]) < 2:
                return []
            return result_list[0][1]

        if len(result_list) < 1:
            return []
        return result_list[0]

    def _get_custom_sql_column_names(self, result_list):
        """
        Determine the column names belonging to the data rows of a custom_sql
        statement, so that item_columns/value_column can be given as column
        names instead of numeric indices.

        Args:
            result_list (list): The value produced by
                list(self.output_statement_result(...)) for this statement.

        Returns:
            tuple[str, ...] | None: Column names in result order, or None if
            they could not be determined (e.g. the query returned no columns,
            or the DB driver did not report a cursor description).
        """
        if self.backend == "postgres":
            # See _extract_custom_sql_data_rows() above for the nesting:
            # result_list[0][0] is the single-element list containing the
            # column header tuple, so result_list[0][0][0] is that tuple.
            if not result_list or not result_list[0] or not result_list[0][0]:
                return None
            return result_list[0][0][0]

        # All other backends: names were collected by query() into
        # self.last_column_names (one entry per executed SQL part), since
        # their query() implementations don't include a header row in the
        # actual result data.
        column_names = self.last_column_names
        if not column_names:
            return None
        return column_names[0]

    def _resolve_custom_sql_column(self, column_ref, column_names, check_header):
        """
        Resolve one item_columns/value_column entry from agent_db.yaml to a
        numeric column index.

        Args:
            column_ref (int | str): Either a 0-based column index, or a
                column name as it appears in the SQL result.
            column_names (tuple[str, ...] | None): Column names for the
                current statement, or None if unavailable.
            check_header (str): Statement name, used for error messages only.

        Returns:
            int: The resolved 0-based column index.

        Raises:
            ValueError: If a column name was given but could not be resolved.
        """
        if isinstance(column_ref, bool):
            # bool is a subclass of int in Python; guard against silently
            # accepting True/False as column index 1/0.
            raise ValueError(
                f"Statement {check_header}: item_columns/value_column entries "
                f"must be an integer index or a column name string, "
                f"got: {column_ref!r}"
            )

        if isinstance(column_ref, int):
            return column_ref

        if isinstance(column_ref, str):
            if column_names is None:
                raise ValueError(
                    f"Statement {check_header}: column name '{column_ref}' was "
                    f"used in item_columns/value_column, but no column names "
                    f"could be determined for this statement/backend. Use a "
                    f"numeric column index instead, or check the SQL statement."
                )
            try:
                return column_names.index(column_ref)
            except ValueError:
                raise ValueError(
                    f"Statement {check_header}: column '{column_ref}' not "
                    f"found in result columns {list(column_names)}."
                )

        raise ValueError(
            f"Statement {check_header}: item_columns/value_column entries "
            f"must be an integer index or a column name string, "
            f"got: {column_ref!r}"
        )

    def _output_custom_sql_multiline(self, check_header, result_list, state_statement_cfg):
        """
        Output one JSON line per data row for a custom_sql statement configured
        for multiline mode (item_columns + value_column in agent_db.yaml).

        For every row returned by the SQL statement, the item name is built by
        joining the configured item_columns (and, optionally, item_prefix), and
        the value is taken from value_column. Every row is written out as its
        own <<<custom_sql>>> JSON entry, so checkmk discovers one service per row.

        item_columns and value_column may each be given either as a 0-based
        column index (int) or as a column name (str), e.g.:
            item_columns: [1]        or   item_columns: ["name"]
            value_column: 4          or   value_column: "population"
        Mixing both styles within item_columns is fine, e.g. [0, "district"].

        Args:
            check_header (str): The header for the output (always "custom_sql" here).
            result_list (list): The value produced by
                list(self.output_statement_result(...)) for this statement.
            state_statement_cfg (dict): Configuration of the current statement
                from agent_db.yaml (must contain "item_columns" and "value_column").

        Returns:
            None
        """
        item_columns_cfg = state_statement_cfg["item_columns"]
        value_column_cfg = state_statement_cfg["value_column"]
        item_prefix = state_statement_cfg.get("item_prefix")
        item_column_separator = state_statement_cfg.get("item_column_separator", " ")

        data_rows = self._extract_custom_sql_data_rows(result_list)

        if not data_rows:
            self.log.debug(
                f"Statement {check_header}: no data rows returned, nothing to output "
                f"for multiline custom_sql."
            )
            return

        column_names = self._get_custom_sql_column_names(result_list)

        try:
            item_columns = [
                self._resolve_custom_sql_column(col, column_names, check_header)
                for col in item_columns_cfg
            ]
            value_column = self._resolve_custom_sql_column(
                value_column_cfg, column_names, check_header
            )
        except ValueError as e:
            self.log.error(str(e))
            return

        for row in data_rows:
            try:
                item_parts = [str(row[idx]).strip() for idx in item_columns]
            except IndexError:
                self.log.error(
                    f"Statement {check_header}: item_columns {item_columns} out of "
                    f"range for row with {len(row)} columns: {row}"
                )
                continue

            item_name = item_column_separator.join(item_parts)
            if item_prefix:
                item_name = f"{item_prefix}{item_column_separator}{item_name}"

            try:
                value = row[value_column]
            except IndexError:
                self.log.error(
                    f"Statement {check_header}: value_column {value_column} out of "
                    f"range for row with {len(row)} columns: {row}"
                )
                continue

            row_checkoutput = {
                "backend": self.backend,
                "backend_service_prefix": self.backend_service_prefix,
                "db_cstr": self.db_cstr,
                "statement_name": check_header,
            }
            row_checkoutput.update(state_statement_cfg)
            # item/value are computed per row and must win over any (unused)
            # static "item"/"value" key that might still be present in the yaml.
            row_checkoutput["item"] = item_name
            row_checkoutput["value"] = value

            sys.stdout.write(json.dumps(row_checkoutput) + "\n")

    @property
    def separator_char(self):
        # NOTE: self.separator is set for every statement.
        # TODO: This is really indicative that the entire printing
        #       logic should be extracted into its own class.
        #       However, as the separator is defined by statement,
        #       the DBStrategy classes need to be split up
        #       into several classes.
        if self.separator == "sep(124)":
            separator = "|"
        elif self.separator == "sep(09)":
            separator = "\t"
        elif self.separator == "sep(59)":
            separator = ";"
        elif self.separator == "sep(0)":
            separator = "\0"
        else:
            separator = " "
        return separator

    @staticmethod
    def _column_names_from_cursor(cursor):
        """
        Read the column names of the last executed statement from the cursor's
        DB-API "description" attribute (standard across psycopg2, pyodbc,
        mysql-connector, cx_Oracle/oracledb, ...).

        Returns:
            tuple[str, ...] | None: Column names, or None if not available
            (e.g. the statement did not return a result set).
        """
        if cursor.description is None:
            return None
        return tuple(desc[0] for desc in cursor.description)

    def query(self, cursor, sqlstatement):
        """
        Run an SQL statement with an open cursor.

        Overriding this method allows different strategies for different DBs
        """
        if sqlstatement.startswith("BEGIN"):
            sqls = [sqlstatement]
        else:
            sqls = sqlstatement.split(";")

        self.last_column_names = []
        for sql in sqls:
            cursor.execute(sql)
            self.last_column_names.append(self._column_names_from_cursor(cursor))
            ret = cursor.fetchall()
            yield ret

    def format_error_message(self, db_cstr, exception, timeout=False):
        if timeout:
            message = (
                f"Connection to {self.backend_service_prefix} DB '{db_cstr}' timed out after "
                f"{self.db_cursor_timeout_sec} seconds. Port {self.db_port}/TCP reachable from checkmk server?"
            )
        else:
            message = f"Error while connecting to {self.backend_service_prefix} DB '{db_cstr}'. Exception:\n{exception}"

        return self.FormattedErrorMessage(message)

    def print_backend_connection_time(
        self, backend: str, db_cstr: str, connection_time: float, error=None
    ):
        """
        Print the backend_connection_time statment statistics.

        Args:
            db_cstr: The connection string of the database.
            connection_time: The time taken to establish the connection.
            error: The error message if the connection failed.
        """
        separator = 0
        if error:
            # cast error to string
            error = str(error)

        connection_stats = {
            "db_cstr": db_cstr,
            "connection_time": connection_time,
            "error": error,
        }
        print(self.cmk_header(f"{backend}_connection_time", separator))
        # if error:
        #    print(f"{db_cstr} {connection_time} {error}", file=sys.stdout)
        # else:
        #    print(f"{db_cstr} {connection_time}", file=sys.stdout)
        print(json.dumps(connection_stats))

    def print_db_stats(self, db_cstr, statement, stats):
        """
        Print the agent_db_stats statment statistics.

        Args:
            db_cstr: The connection string of the database.
            statement: The SQL statement being executed.
            stats: The statistics data to print as json checkoutput.
        """
        print("<<<agent_db_stats:sep(0)>>>")
        db_stats = {db_cstr: {statement: stats}}
        print(json.dumps(db_stats))

    def exec_sql(
        self, db, statement, sqlstatement, sqlstatement_timeout, cache_time_sec=None
    ):
        """
        Execute a Query against the given db conn object. Open a cursor, handle timeout, and utilize caching if specified.

        Args:
            db: The database connection object.
            statement: The statement identifier.
            sqlstatement: The SQL statement to execute.
            sqlstatement_timeout: The timeout value for the SQL statement execution.
            cache_time_sec: The time duration to cache the query result (optional).

        Returns:
            A tuple containing the query results and the modification time of the cache file (if caching is enabled).
        """
        stats = {
            "status": None,
            "runtime": None,
            "exception": None,
            "timeout": sqlstatement_timeout,
        }
        results = []
        cache_key = None
        mtime_cache_file = None

        if cache_time_sec is not None:
            # Generate a cache key for the SQL statement
            cache_key = cache.generate_cache_key(self.db_host, self.db_cstr, statement)
            # Attempt to retrieve the query result from the cache
            cache_result = cache.get_cache(cache_key, self.cache_dir, cache_time_sec)
            if cache_result is not None:
                # Cache hit, use the cached result
                self.log.debug(
                    f"Cache hit for: {self.db_host} {self.db_cstr} {statement}"
                )
                mtime_cache_file, cached_data = cache_result
                stats["status"] = "OK"
                stats["runtime"] = 0.0
                if isinstance(cached_data, dict) and "results" in cached_data:
                    # Cache format written by this version (includes column names,
                    # needed to resolve item_columns/value_column given as names).
                    results = cached_data["results"]
                    self.last_column_names = cached_data.get("column_names")
                else:
                    # Backward compatible with cache files written by older
                    # agent_db versions (plain results list, no column names).
                    results = cached_data
                    self.last_column_names = None
                self.print_db_stats(self.db_cstr, statement, stats)
                return (results, mtime_cache_file)

        # Define a function to run the query in a separate thread
        def run_query():
            nonlocal results, stats
            try:
                cursor = db.cursor()
                start_time = time.time()  # Record start time

                for result in self.query(cursor, sqlstatement):
                    results.append(result)

                end_time = time.time()  # Record end time
                stats["runtime"] = end_time - start_time  # Calculate runtime
                stats["status"] = "OK"
                if cache_time_sec is not None and cache_key is not None:
                    # Write the result to cache
                    self.log.debug(f"Writing cache for: {cache_key}")
                    cache.write_cache(
                        self.cache_dir,
                        cache_key,
                        {
                            "results": results,
                            "column_names": self.last_column_names,
                        },
                    )
            except Exception as e:
                self.log.error(f"Error running query {statement}: {str(e)}")
                stats["status"] = "CRIT"
                stats["exception"] = str(e)
            finally:
                cursor.close()

        # Proceed with existing thread logic to execute query if not loaded from cache
        stop_event = threading.Event()
        query_thread = threading.Thread(target=run_query)
        query_thread.start()
        query_thread.join(timeout=sqlstatement_timeout)

        if query_thread.is_alive():
            stop_event.set()
            self.log.error(f"Query {statement} took to long and has been terminated")
            stats["status"] = "CRIT"
            stats["exception"] = "Query took too long and has been terminated"

        print("<<<agent_db_stats:sep(0)>>>")
        stats = {self.db_cstr: {statement: stats}}
        print(json.dumps(stats))

        # self.connection.close()
        return (results, mtime_cache_file)


class PortChecker:
    def __init__(self, host: str, port: int, timeout: int):
        self.host = host
        self.port = port
        self.timeout = timeout

    def is_port_open(self) -> bool:
        """Check if the specified TCP port is open."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)

        try:
            result = sock.connect_ex((self.host, self.port))
            return result == 0  # True if the port is open, otherwise False
        finally:
            sock.close()  # Ensure the socket is closed gracefully
