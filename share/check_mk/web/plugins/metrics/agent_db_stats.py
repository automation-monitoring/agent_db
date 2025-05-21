#!/usr/bin/env python3

from cmk.gui.i18n import _

from cmk.gui.plugins.metrics import (
    metric_info,
)

_statements = [
    "mssql_availability_groups",
    "mssql_backup",
    "mssql_blocked_sessions",
    "mssql_connections",
    "mssql_counters",
    "mssql_databases",
    "mssql_datafiles",
    "mssql_instance",
    "mssql_jobs",
    "mssql_maxservermem",
    "mssql_mirroring",
    "mssql_tablespaces",
    "mssql_transactionlogs",
    "mssql_version",
    "mysql_capacity",
    "mysql_global",
    "mysql_slaves",
    "mysql_threads_connected",
    "oracle_asm_diskgroup",
    "oracle_custom_statement",
    "oracle_dataguard_stats",
    "oracle_instance",
    "oracle_jobs",
    "oracle_locks",
    "oracle_logswitches",
    "oracle_longactivesessions",
    "oracle_longterm_statement",
    "oracle_performance",
    "oracle_processes",
    "oracle_recovery_area",
    "oracle_recovery_status",
    "oracle_rman",
    "oracle_sessions",
    "oracle_systemparameter",
    "oracle_tablespaces",
    "oracle_undostat",
    "oracle_version",
    "postgres_bloat",
    "postgres_connections",
    "postgres_cache_hitratio",
    "postgres_locks",
    "postgres_query_duration",
    "postgres_sessions",
    "postgres_stat_database",
    "postgres_stats",
    "postgres_txn_wraparound",
    "postgres_version",
]

for statement in _statements:
    metric_info[f"query_runtime_{statement}"] = {
        "title": _(f"Query Runtime {statement}"),
        "unit": "s",
        "color": "#42fc9c",
    }
