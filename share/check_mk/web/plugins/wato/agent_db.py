#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

from cmk.gui.i18n import _
from cmk.gui.plugins.wato import (
    HostRulespec,
    IndividualOrStoredPassword,
    rulespec_registry,
)
from cmk.gui.valuespec import (
    Dictionary,
    TextInput,
    Integer,
    FixedValue,
    DropdownChoice,
    CascadingDropdown,
    ListOfStrings,
    ListChoice,
    Transform,
)
from cmk.gui.plugins.wato.datasource_programs import RulespecGroupDatasourceProgramsApps


def _add_default_pkg_choice(additional_choices=[]):
    def_custom_choices = [
        ("custom_a", _("Custom Package A")),
        ("custom_b", _("Custom Package B")),
        ("custom_c", _("Custom Package C")),
    ]
    return [
        (
            # To ensure that this backend parameter is correctly interpreted in agent_db.py, ensure that the key ends with '_pkgs'
            "default_pkgs",
            ListChoice(
                title=_("Default Statement Packages"),
                help=_(
                    "Select your packages.<br>A statement package is used to summarize statements in agent_db.yml that are to be executed on the database server"
                ),
                choices=[
                    ("basic", _("Basic")),
                    ("standard", _("Standard")),
                    ("performance", _("Performance")),
                ]
                + def_custom_choices
                + additional_choices,
                default_value=["standard"],
            ),
        ),
    ]


def _add_oracle_specific_pkg_choice():
    oracle_specific_choices = [
        ("oracle_pdb", _("Oracle Pluggable Database")),
        ("oracle_rac_inst", _("Oracle RAC Instance (Node)")),
        ("oracle_rac_db", _("Oracle RAC Database (Cluster)")),
        #    ("oracle_asm", _("Oracle Automatic Storage Management (ASM)")),
    ]

    return [
        (
            # To ensure that this backend parameter is correctly interpreted in agent_db.py, ensure that the key ends with '_pkgs'
            "oracle_pkgs",
            ListChoice(
                title=_("Oracle Specific Statement Packages"),
                help=_(
                    "<b>Oracle Pluggable Database</b><br>\
                    Enable Oracle Pluggable Database Monitoring<br>\
                    <br><b>Oracle RAC Instance (Node)</b><br>\
                    Should be enabled for each RAC Node<br>\
                    <br><b>Oracle RAC Database (Cluster)</b><br>\
                    Should be activated on the RAC database itself to prevent checks such as tablespaces from being executed on each node<br>\
                "
                ),
                choices=oracle_specific_choices,
            ),
        ),
    ]


def _add_oracle_asm_credentials():
    return [
        (
            "asm_credentials",
            Dictionary(
                title=_("ASM Credentials"),
                help=_(
                    "Credentials for Oracle ASM (Automatic Storage Management). If defined, ASM will be monitored as ASM+ with sysdba privileges."
                ),
                elements=[
                    (
                        "asm_user",
                        TextInput(
                            title=_("ASM User"),
                            help=_("User to connect to Oracle ASM"),
                            allow_empty=False,  # Allowing this to be optional
                        ),
                    ),
                    (
                        "asm_password",
                        IndividualOrStoredPassword(
                            title=_("ASM Password"),
                            help=_("Password to connect to Oracle ASM"),
                            allow_empty=False,  # Allowing this to be optional
                        ),
                    ),
                ],
                optional_keys=[],
            ),
        ),
    ]


def _add_custom_packages():
    return [
        (
            # To ensure that this backend parameter is correctly interpreted in agent_db.py, ensure that the key ends with '_pkgs'
            "custom_pkgs",
            ListOfStrings(
                title=_("Custom Statement Packages"),
                orientation="horizontal",
                help=_(
                    "<b>Custom Packages</b><br>\
                            You can define Custom Packages to assign statements within agent_db.yml<br>\
                            <br><b>Checkmk hint about the usage of 'List of Strings':</b><br>\
                            "
                ),
                size=30,
                allow_empty=True,
            ),
        ),
    ]


def _add_port(port):
    return [
        (
            "port",
            Transform(
                TextInput(
                    title=_("TCP Port"),
                    help=_("Port number that server is listening on."),
                    default_value=str(port),
                    size=6,
                ),
                forth=lambda v: "%d" % v if type(v) is int else v,
            ),
        )
    ]


def _add_monitor_all(default_exclude_dbs=[]):
    return [
        (
            "monitor_all",
            Dictionary(
                title=_("Monitor all DBs"),
                elements=[
                    ("monitor_all", FixedValue(title=_("Monitor all DBs"), value=True)),
                    (
                        "exclude_dbs",
                        ListOfStrings(
                            title=_("Exclude the following DBs"),
                            default_value=default_exclude_dbs,
                        ),
                    ),
                ],
                optional_keys=["exclude_dbs"],
                hidden_keys=["monitor_all"],
            ),
        )
    ]


def _valuespec_special_agents_db():
    default_optional_keys_backend = ["default_pkgs", "custom_pkgs", "monitor_all"]
    return Dictionary(
        title=_("Database Special Agent"),
        help=_(
            "Gather data remotely from supported db backends (Oracle, MSSQL, MySQL, Postgres)"
        ),
        elements=[
            (
                "db_backend",
                CascadingDropdown(
                    choices=[
                        (
                            "cmk_mssql",
                            _("MSSQL"),
                            Dictionary(
                                elements=[
                                    (
                                        "instance",
                                        TextInput(
                                            title=_("Instance"),
                                            help=_(
                                                "In case of a MSSQL named instance, the instance name must be specified here. Otherwise, leave <u><b>empty!</b></u>.<br>\
                                                If you monitor databases using availability groups (avg), it is not necessary to specify an instance, because the mssql avg listener configuration defines the underlying mssql instances."
                                            ),
                                            size=20,
                                            default_value=None,
                                        ),
                                    ),
                                ]
                                + _add_port(1433)
                                + _add_default_pkg_choice()
                                + _add_custom_packages()
                                + _add_monitor_all(
                                    default_exclude_dbs=["tempdb", "model", "msdb"]
                                ),
                                optional_keys=default_optional_keys_backend
                                + ["instance"],
                            ),
                        ),
                        (
                            "cmk_mysql",
                            _("MySQL"),
                            Dictionary(
                                elements=[]
                                + _add_port(3306)
                                + _add_default_pkg_choice()
                                + _add_custom_packages(),
                                optional_keys=default_optional_keys_backend,
                            ),
                        ),
                        (
                            "cmk_oracle",
                            _("Oracle"),
                            Dictionary(
                                elements=[]
                                + _add_port(1521)
                                + _add_oracle_asm_credentials()
                                + _add_default_pkg_choice()
                                + _add_oracle_specific_pkg_choice()
                                + _add_custom_packages(),
                                optional_keys=default_optional_keys_backend
                                + ["oracle_pkgs", "asm_credentials"],
                            ),
                        ),
                        (
                            "cmk_postgres",
                            _("Postgres"),
                            Dictionary(
                                elements=[]
                                + _add_port(5432)
                                + _add_default_pkg_choice()
                                + _add_custom_packages()
                                + _add_monitor_all(default_exclude_dbs=[]),
                                optional_keys=default_optional_keys_backend,
                            ),
                        ),
                    ],
                    default_value="cmk_oracle",
                    title=_("Database Backend"),
                ),
            ),
            (
                "db_cstr",
                ListOfStrings(
                    title=_("Connection String"),
                    orientation="horizontal",
                    help=_(
                        "<b>Oracle</b>: SID or Service Name.<br>\
                         If the connection string starts with a '(' then it is assumed to be a TNS entry and it will override the host and port settings.<br>\
                            <b>MySQL</b>: Database name.<br>\
                            <b>MSSQL</b>: Database name.<br>\
                            <b>Postgres</b>: Database name.<br><br>\
                            <b>Checkmk Custom Host Attributes</b><br>\
                            You can use custom host attributes to define the connection string directly in the host configuration<br>\
                            Use the format: <<my_custom_host_attr_id>><br>\
                            Multiple custom host attributes are not supported in this ruleset, only the first entry is used.<br>\
                            If you like to specify several databases for a host you can split them with a semicolon (;)<br>\
                            Example: <b>db1;db2;db3</b><br><br>\
                            <b>Checkmk hint about the usage of 'List of Strings':</b><br>\
                            "
                    ),
                    size=80,
                    allow_empty=True,
                ),
            ),
            (
                "user",
                TextInput(
                    title=_("User"),
                    help=_("User to connect to the Database"),
                    allow_empty=False,
                ),
            ),
            (
                "password",
                IndividualOrStoredPassword(
                    title=_("Password"),
                    help=_("Password to connect to the Database"),
                    allow_empty=False,
                ),
            ),
            (
                "enforce_dns_lookup",
                FixedValue(
                    value=True,
                    title=_("Enforce DNS Lookup"),
                    totext=_("enabled"),
                    help=_(
                        "Enable to enforce DNS lookup for each special agent run.\
                         No Checkmk DNS cache or explicit IP address from checkmk host configuration is used."
                    ),
                ),
            ),
            (
                "loglevel",
                DropdownChoice(
                    title=_("Loglevel"),
                    choices=[
                        ("debug", _("Debug")),
                        ("info", _("Info")),
                        ("warning", _("Warning")),
                        ("error", _("Error")),
                        (None, _("No logging")),
                    ],
                    default_value="error",
                ),
            ),
        ],
        optional_keys=["db_cstr", "db_backend", "enforce_dns_lookup"],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsApps,
        # match_type="all",
        name="special_agents:db",
        valuespec=_valuespec_special_agents_db,
    )
)
