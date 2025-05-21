#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

import argparse
import sys
import os
import importlib
import json
import base64
import requests
import yaml
import pprint
import logging

import cmk.utils.password_store


def _get_automation_secret(username="automation"):
    """Get automation secret for the given user. Default user is automation"""
    omd_root = os.environ["OMD_ROOT"]
    # If automation.secret file for user exists, read credentials from there
    secret_file = f"{omd_root}/var/check_mk/web/{username}/automation.secret"
    if os.path.exists(secret_file):
        secret = open(secret_file).read().strip()
        return secret
    else:
        return False


class AgentDBLog:
    def __init__(self, logfile, loglevel):
        """Initialize logging"""
        self.loglevel = loglevel
        self.log = logging.getLogger(__name__)
        if loglevel is not None:
            self.log.setLevel(self.loglevel.upper())
        else:
            logging.disable()

        # Create a custom formatter that includes the module name
        class FormatterWithClassName(logging.Formatter):
            def format(self, record):
                record.module_name = record.name
                return super().format(record)

        formatter = FormatterWithClassName(
            "%(asctime)s %(levelname)s [%(module_name)s]: %(message)s"
        )

        # Check if the file handler already exists before adding it
        if not any(
            isinstance(handler, logging.FileHandler) for handler in self.log.handlers
        ):
            file_handler = logging.FileHandler(logfile)
            file_handler.setFormatter(formatter)
            self.log.addHandler(file_handler)

        # Pin the logger to the class
        AgentDBLog.logger = self.log

    @staticmethod
    def log_error_and_exit(message):
        """Static method to log an error and exit."""
        if AgentDBLog.logger is not None:
            print(message, file=sys.stderr)
            AgentDBLog.logger.critical(message)
            sys.exit(1)
        else:
            raise RuntimeError("Logger has not been initialized.")


class CMKInstance:
    """Interact with checkmk instance"""

    def __init__(self, url=None, username="automation", password=None):
        """Initialize a REST-API instance. URL, User and Secret can be automatically taken from local site if running as site user.

        Args:
            site_url: the site URL
            api_user: username of automation user account
            api_secret: automation secret

        Returns:
            instance of CMKRESTAPI
        """
        if not url:
            # site_url = _site_url()
            api_version = "1.0"
            # use local siteurl from $HOME/etc/apache/conf.d/listen-port.conf
            omd_root = os.environ["OMD_ROOT"]
            omd_site = os.environ["OMD_SITE"]
            f = open(f"{omd_root}/etc/apache/listen-port.conf", "r").readlines()
            for line in f:
                if line.startswith("Listen"):
                    cmk_local_apache = line.split(" ")[1].strip()
            siteurl = f"http://{cmk_local_apache}/{omd_site}"

            self._api_url = f"{siteurl}/check_mk/api/{api_version}"
        else:
            self._api_url = url

        if not password:
            secret = _get_automation_secret(username)
        else:
            secret = password

        self.headers = {
            "Content-Type": "application/json",
        }

        self._session = requests.session()
        self._session.headers["Authorization"] = f"Bearer {username} {secret}"
        self._session.headers["Accept"] = "application/json"

    def _trans_resp(self, resp):
        try:
            data = resp.json()
        except json.decoder.JSONDecodeError:
            data = resp.text
            print(f"JSONDecodeError for data: {data}")
        return data, resp

    def _request_url(self, method, endpoint, data={}, etag=None):
        headers = self.headers
        if etag is not None:
            headers["If-Match"] = etag

        url = f"{self._api_url}/{endpoint}"
        request_func = getattr(self._session, method.lower())

        return self._trans_resp(
            request_func(
                url,
                json=data,
                headers=headers,
                allow_redirects=False,
            )
        )

    def _get_url(self, endpoint, data={}):
        return self._request_url("GET", endpoint, data)

    def _put_url(self, endpoint, etag, data={}):
        return self._request_url("PUT", endpoint, data, etag)

    def _post_url(self, endpoint, data={}):
        return self._request_url("POST", endpoint, data)

    def get_host(self, hostname):
        """Get current host configuration

        Args:
            hostname: cmk hostname

        Return:
            data: {hostconfig}
        """
        data, resp = self._get_url(
            f"objects/host_config/{hostname}", data={"effective_attributes": "false"}
        )
        if resp.status_code == 200:
            return data
        resp.raise_for_status()

    def get_host_attributes(self, hostname):
        return self.get_host(hostname)["extensions"]["attributes"]

    def get_custom_host_attr(self, hostname, custom_host_attr_var):
        return self.get_host_attributes(hostname).get(custom_host_attr_var, None)

    def get_etag(self, hostname):
        """Get current etag value for host"""
        data, resp = self._get_url(
            f"objects/host_config/{hostname}", data={"effective_attributes": "false"}
        )
        if resp.status_code == 200:
            return resp.headers["etag"]
        resp.raise_for_status()

    def host_exists(self, hostname):
        """Check if host exists"""
        host = self.get_host(hostname)
        return host


def deserialize_agent_db_arguments(base64_params):
    # Decode base64 string
    json_params = base64.b64decode(base64_params).decode()

    # Load JSON data into a Python dictionary
    return json.loads(json_params)


def resolve_custom_host_attr(param, value, hostname):
    """
    Resolves a custom host attribute from a parameter specification.

    Args:
    param (str): The parameter name to check.
    value: The value associated with the parameter which might be a list or string.
    hostname (str): The hostname used to fetch the custom attribute.

    Returns:
    str or None: The resolved custom host attribute value or None if not applicable.
    """
    if isinstance(value, list) and param == "db_cstr":
        value = value[0]

    if isinstance(value, str) and value.startswith("<<") and value.endswith(">>"):
        custom_host_attr = value.strip("<<>>")
        cmkinst = CMKInstance()
        custom_host_attr_value = cmkinst.get_custom_host_attr(
            hostname, custom_host_attr
        )
        return custom_host_attr_value
    # Instead of using the cmk api, it would be better to use the cmk.base.config module, but it doesn't seem to work for custom host attributes at the moment
    # test = config.CEEHostConfig(config_cache=config_cache, hostname="db-oracle")

    return None  # Return None if no conditions are met or the value is not resolved


class DBHandler:
    def __init__(self, ipaddress, args, params, log, statement_config, backend_module):

        self.ipaddress = ipaddress
        self.args = args
        self.params = params
        self.log = log
        self.statement_config = statement_config
        self.backend_module = backend_module
        # Get the backend and backend parameters
        # e.g. ("cmk_oracle", {'port': 1521, 'default_pkgs': ['basic', 'standard', 'performance']})
        self.backend, self.backend_params = self.params["db_backend"]

    def resolve_custom_host_attrs(self, hostname):
        for param, value in self.params.items():
            resolved_custom_host_attr = resolve_custom_host_attr(param, value, hostname)
            if resolved_custom_host_attr:
                self.params[param] = resolved_custom_host_attr

        for key, val in self.backend_params.items():
            resolved_custom_host_attr = resolve_custom_host_attr(key, val, hostname)
            if resolved_custom_host_attr:
                self.backend_params[key] = resolved_custom_host_attr

    def determine_db_connection_string(self):
        if "db_cstr" in self.params:
            db_cstr = self.params["db_cstr"]
        else:
            if self.backend == "cmk_mysql":
                db_cstr = "mysql"
            elif self.backend == "cmk_mssql":
                db_cstr = "master"
            elif self.backend == "cmk_postgres":
                db_cstr = "postgres"
            else:
                AgentDBLog.log_error_and_exit(
                    "No DB connect string provided. Please define either via Checkmk ruleset or custom host attribute."
                )

        if isinstance(db_cstr, str):
            if ";" in db_cstr:
                db_cstr = db_cstr.split(";")
            else:
                db_cstr = [db_cstr]
        return db_cstr

    def _get_backend_params(self, cstr):
        db_backend_params = {
            "loglevel": self.log.loglevel,
            "db_host": self.ipaddress,
            "db_hostname": self.args.hostname,
            "db_user": self.params["user"],
            "db_pass": self.params["password"],
            "db_cstr": cstr,
            "db_port": int(self.backend_params["port"]),
            "db_cursor_timeout_sec": self.statement_config.get(
                "db_cursor_timeout_sec", 3
            ),
        }
        if "instance" in self.backend_params:
            db_backend_params["db_instance"] = self.backend_params["instance"]
            self.log.log.debug(f"Instance defined: {self.backend_params['instance']}")
        else:
            db_backend_params["db_instance"] = None
            self.log.log.debug(f"No instance defined.")
        return db_backend_params

    def process_db_connections(self):

        # Special handling for oracle_asm_diskgroup statement, because it needs to be executed only once with a special connection object
        try:
            statement_desc = self.statement_config[self.backend]["statement_desc"]
        except KeyError:
            AgentDBLog.log_error_and_exit(
                f"No statement_desc found in agent.yml for backend {self.backend}",
            )

        if "oracle_asm_diskgroup" in statement_desc:
            # Execute self._process_single_connection for all connection strings without "oracle_asm_diskgroup"
            asm_diskgroup_value = statement_desc.pop("oracle_asm_diskgroup")

            db_cstr_list = self.determine_db_connection_string()
            for cstr in db_cstr_list:
                self._process_single_connection(cstr)

            # Modify statement_desc to only contain "oracle_asm_diskgroup"
            statement_desc.clear()
            statement_desc["oracle_asm_diskgroup"] = asm_diskgroup_value

            # Execute self._process_single_connection with the first connection string for "oracle_asm_diskgroup"
            # Since it doesen't matter which connection string is used for "oracle_asm_diskgroup", because ASM+ is used we do it currently that way.
            # Idea: It would be better to have the logic in one place and only “mode=oracledb.SYSDBA,” should be a parameter for the connection object.
            # Then def _select_connection(self, state_statement_cfg, params): in cmk_oracle.py would be obsolete.

            if db_cstr_list:
                self._process_single_connection(db_cstr_list[0])

        else:
            db_cstr_list = self.determine_db_connection_string()
            if self.backend_params.get("monitor_all"):
                # Default cstr is the first in the list and will be used for the initial connection
                # e.g. mssql: db_cstr = 'master'
                db_backend_params = self._get_backend_params(db_cstr_list[0])
                strategy = self.backend_module.DBStrategy(**db_backend_params)

                if isinstance(strategy.connection, strategy.FormattedErrorMessage):
                    # If connection object is from type FormattedErrorMessage, log error and exit special agent directly
                    AgentDBLog.log_error_and_exit(
                        f"Could not connect to DB {db_cstr_list[0]} to get list of DBs - {strategy.connection}"
                    )
                all_dbs = strategy.list_all_dbs()
                strategy.close_db_connection()
                exclude_dbs = self.backend_params["monitor_all"].get("exclude_dbs", [])
                db_cstr_list = [db for db in all_dbs if db not in exclude_dbs]
            for cstr in db_cstr_list:
                self._process_single_connection(cstr)

    def _process_single_connection(self, cstr):
        db_backend_params = self._get_backend_params(cstr)

        self.log.log.debug(f"Call {self.backend} DBStrategy with following parameters:")
        self.log.log.debug(
            pprint.pformat(db_backend_params).replace(
                db_backend_params["db_pass"], "*****"
            )
        )

        strategy = self.backend_module.DBStrategy(**db_backend_params)
        # Execute statements only if connection object is available
        result = strategy._select_connection({}, self.params)

        if result is not None and not isinstance(
            result, strategy.FormattedErrorMessage
        ):
            strategy.exec_statements(
                self.statement_config[self.backend], self.backend_params, self.params
            )
            strategy.close_db_connection()


def main():
    """Main function"""

    cmk.utils.password_store.replace_passwords()

    parser = argparse.ArgumentParser(description="Checkmk DB Special Agent")
    parser.add_argument(
        "--backend",
        choices=["cmk_oracle", "cmk_mssql", "cmk_mysql", "cmk_postgres"],
        help="Choose DB backend (cmk_oracle, cmk_mssql, cmk_mysql, cmk_postgres)",
    )
    parser.add_argument(
        "--base64args",
        required=False,
        help="Base64 encoded arguments",
        default="eyAieCIgOiAieSIgfQo=",
    )
    parser.add_argument(
        "--hostname",
        required=False,
        help="Hostname",
        default="localhost",
    )
    parser.add_argument(
        "--ipaddress",
        required=True,
        help="IP Address",
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Password",
    )
    parser.add_argument(
        "--asm_password",
        required=False,
        help="ASM Password",
    )
    args = parser.parse_args()

    OMD_ROOT = os.environ["OMD_ROOT"]

    if args.base64args:
        params = deserialize_agent_db_arguments(args.base64args)

    if args.password:
        params["password"] = args.password

    if args.asm_password:
        if "asm_credentials" in params["db_backend"][1]:
            params["db_backend"][1]["asm_credentials"]["asm_password"] = args.asm_password

    if args.hostname:
        hostname = args.hostname

    if args.ipaddress:
        ippaddress = args.ipaddress
        if params.get("enforce_dns_lookup", False):
            # Set ipaddress to hostname and let the special agent resolve it to an IP address not checkmk cached ip
            ippaddress = args.hostname

    loglevel = params.get("loglevel", "error")

    logpath = f"{OMD_ROOT}/var/log/agent_db"
    if not os.path.exists(logpath):
        os.makedirs(logpath)

    log = AgentDBLog(f"{logpath}/{hostname}.log", loglevel)

    configfile = f"{OMD_ROOT}/etc/agent_db.yml"
    if os.path.exists(configfile):
        with open(configfile, "r") as f:
            statement_config = yaml.safe_load(f)
    else:
        AgentDBLog.log_error_and_exit(f"Config file {configfile} not found.")

    backend_module = importlib.import_module(
        f"cmk.special_agents.db.{params['db_backend'][0]}"
    )

    handler = DBHandler(ippaddress, args, params, log, statement_config, backend_module)
    handler.resolve_custom_host_attrs(hostname)
    handler.process_db_connections()


if __name__ == "__main__":
    main()
