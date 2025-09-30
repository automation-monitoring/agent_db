#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

from cmk.rulesets.v1 import Help, Label, Title
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic
from cmk.rulesets.v1.form_specs import(
    BooleanChoice,
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    DefaultValue,
    Dictionary,
    DictElement,
    FixedValue,
    List,
    migrate_to_password,
    MultipleChoice,
    MultipleChoiceElement,
    Password,
    SingleChoice,
    SingleChoiceElement,
    String,
)

# TODO: Fix all multiline strings in this file!

def element_monitor_all(required=False, default_exclude_dbs=[]):
    return {
        "monitor_all" :
        DictElement(
            parameter_form=Dictionary(
                    title=Title("Monitor all DBs"),
                    elements={
                        # TODO: Find a way to hide monitor_all.
                        "monitor_all" : DictElement(
                                parameter_form=FixedValue(value=True),
                                required=True,
                            ),
                        "exclude_dbs" : DictElement(
                                parameter_form=List(
                                        title=Title("Exclude the following DBs"),
                                        #prefill=DefaultValue(default_exclude_dbs), #TODO: List hat kein default_value oder prefill mehr. was machen?
                                        element_template=String(),
                                    ),
                                required=False,
                            ),

                    }
                ),
            required=required,
        ),
    }


def element_custom_packages(required=False):
    return {
        "custom_pkgs" :
        DictElement(
            parameter_form=List(
                title=Title("Custom Statement Packages"),
                help_text=Help(
                    "<b>Custom Packages</b><br>\
                            You can define Custom Packages to assign statements within agent_db.yml<br>\
                            <br><b>Checkmk hint about the usage of 'List of Strings':</b><br>\
                            "
                    ),
                editable_order=False,
                element_template=String(),
            ),
            required=required,
        ),
    }


def element_default_pkgs(required=False):
    return {
        "default_pkgs" :
        DictElement(
            parameter_form=MultipleChoice(
                title=Title("Default Statement Packages"),
                help_text=Help(
                    "Select your packages.<br>A statement package is used to summarize statements in agent_db.yml that are to be executed on the database server"
                    ),
                show_toggle_all=True,
                elements=[
                    MultipleChoiceElement(name="basic", title=Title("Basic")),
                    MultipleChoiceElement(name="standard", title=Title("Standard")),
                    MultipleChoiceElement(name="performance", title=Title("Performance")),
                    MultipleChoiceElement(name="custom_a", title=Title("Custom Package A")),
                    MultipleChoiceElement(name="custom_b", title=Title("Custom Package B")),
                    MultipleChoiceElement(name="custom_c", title=Title("Custom Package C")),
                ],
                prefill=DefaultValue(["standard"]),
                ),
            required=required,
        ),
    }


def element_port(port, required=True):
    return {
        "port" :
        DictElement(
            parameter_form=String(
                    title=Title("TCP Port"),
                    help_text=Help("Port number that server is listening on."),
                    prefill=DefaultValue("%d" % port),
                ),
            required=required,
        ),
    }


def element_mssql_instance(required=False):
    return {
        "instance" :
        DictElement(
            parameter_form=String(
                title=Title("Instance"),
                help_text=Help(
                    "In case of a MSSQL named instance, the instance name must be specified here. Otherwise, leave <u><b>empty!</b></u>.<br>\
                    If you monitor databases using availability groups (avg), it is not necessary to specify an instance, because the mssql avg listener configuration defines the underlying mssql instances."
                    ),
            ),
            required=required
        ),
    }


def element_oracle_asm_credentials(required=False):
    return {
        "asm_credentials" :
        DictElement(
            parameter_form=Dictionary(
                title=Title("ASM Credentials"),
                help_text=Help(
                    "Credentials for Oracle ASM (Automatic Storage Management). If defined, ASM will be monitored as ASM+ with sysdba privileges."
                ),
                elements={
                    "asm_user" : DictElement(
                            parameter_form=String(
                                    title=Title("ASM User"),
                                    help_text=Help("User to connect to Oracle ASM"),
                                    #TODO: allow_empty ist in neuer API was?
                                ),
                            required=True,
                        ),
                    "asm_password": DictElement(
                            parameter_form=Password(
                                    title=Title("ASM Password"),
                                    help_text=Help("Password to connect to Oracle ASM"),
                                    #TODO: allow_empty ist in neuer API was? Braucht's das hier?
                                    migrate=migrate_to_password,
                                ),
                            required=True,
                        ),
                }
            ),
            required=required,
        ),
    }


def element_oracle_specific_pkgs(required=False):
    return {
        "oracle_pkgs" :
        DictElement(
            parameter_form=MultipleChoice(
                title=Title("Oracle Specific Statement Packages"),
                help_text=Help(
                    "<b>Oracle Pluggable Database</b><br>\
                    Enable Oracle Pluggable Database Monitoring<br>\
                    <br><b>Oracle RAC Instance (Node)</b><br>\
                    Should be enabled for each RAC Node<br>\
                    <br><b>Oracle RAC Database (Cluster)</b><br>\
                    Should be activated on the RAC database itself to prevent checks such as tablespaces from being executed on each node<br>\
                "
                ),
                elements=[
                    MultipleChoiceElement(
                        name="oracle_pdb",
                        title=Title("Oracle Pluggable Database"),
                    ),
                    MultipleChoiceElement(
                        name="oracle_rac_inst",
                        title=Title("Oracle RAC Instance (Node)"),
                    ),
                    MultipleChoiceElement(
                        name="oracle_rac_db",
                        title=Title("Oracle RAC Database (Cluster)"),
                    ),
                ],
            ),
            required=required,
        ),
    }


def parameter_form_mssql():
    return Dictionary(
                elements={}
                    | element_mssql_instance()
                    | element_port(1433)
                    | element_default_pkgs()
                    | element_custom_packages()
                    | element_monitor_all(),
            )


def parameter_form_mysql():
    return Dictionary(
                elements={}
                    | element_port(3306)
                    | element_default_pkgs()
                    | element_custom_packages(),
            )


def parameter_form_oracle():
    return Dictionary(
                elements={}
                    | element_port(1521)
                    | element_oracle_asm_credentials()
                    | element_default_pkgs()
                    | element_oracle_specific_pkgs()
                    | element_custom_packages(),
            )


def parameter_form_postgres():
    return Dictionary(
            elements={}
                | element_port(5432)
                | element_default_pkgs()
                | element_custom_packages()
                | element_monitor_all(),
        )


def parameter_form_db_backend():
    return CascadingSingleChoice(
            title=Title("Database Backend"),
            elements=[
                CascadingSingleChoiceElement(
                    name="cmk_mssql",
                    title=Title("MSSQL"),
                    parameter_form=parameter_form_mssql(),
                ),
                CascadingSingleChoiceElement(
                    name="cmk_mysql",
                    title=Title("MySQL"),
                    parameter_form=parameter_form_mysql(),
                ),
                CascadingSingleChoiceElement(
                    name="cmk_oracle",
                    title=Title("Oracle"),
                    parameter_form=parameter_form_oracle(),
                ),
                CascadingSingleChoiceElement(
                    name="cmk_postgres",
                    title=Title("Postgres"),
                    parameter_form=parameter_form_postgres(),
                ),
            ],
        )


def parameter_form_db_cstr():
    return List(
            title=Title("Connection String"),
            element_template=String(),
        )


def parameter_form_user():
    return String(
            title=Title("User"),
            help_text=Help("User to connect to the Database"),
        )


def parameter_form_password():
    return Password(
            title=Title("Password"),
            help_text=Help("Password to connect to the Database"),
            migrate=migrate_to_password,
        )


def parameter_form_enforce_dns_lookup():
    return BooleanChoice(
            title=Title("Enforce DNS Lookup"),
            help_text=Help(
                        "Enable to enforce DNS lookup for each special agent run.\
                         No Checkmk DNS cache or explicit IP address from checkmk host configuration is used."
            ),
            prefill=DefaultValue(True),
        )


def parameter_form_loglevel():
    return SingleChoice(
            title=Title("Loglevel"),
            elements=[
                SingleChoiceElement(name="debug", title=Title("Debug")),
                SingleChoiceElement(name="info", title=Title("Info")),
                SingleChoiceElement(name="warning", title=Title("Warning")),
                SingleChoiceElement(name="error", title=Title("Error")),
                SingleChoiceElement(name="none", title=Title("No logging")), #TODO: Berücksichtigen in serversidecall
            ],
            migrate=lambda v: "none" if v is None else v,
            prefill=DefaultValue("error"),
        )


def parameter_form():
    return Dictionary(
        elements={
            "db_backend" : DictElement(
                            parameter_form=parameter_form_db_backend(),
                            required=True,
                        ),
            "db_cstr" : DictElement(
                            parameter_form=parameter_form_db_cstr(),
                            required=False,
                        ),
            "user" : DictElement(
                        parameter_form=parameter_form_user(),
                        required=True,
                    ),
            "password" : DictElement(
                            parameter_form=parameter_form_password(),
                            required=True,
                        ),
            "enforce_dns_lookup" : DictElement(
                                    parameter_form=parameter_form_enforce_dns_lookup(),
                                    required=False,
                                ),
            "loglevel" : DictElement(
                            parameter_form=parameter_form_loglevel(),
                            required=True,
                        ),
        }
    )


rule_spec_special_agent_agent_db = SpecialAgent(
    name="db",
    title=Title("Database Special Agent"),
    topic=Topic.GENERAL,
    parameter_form=parameter_form,
)
