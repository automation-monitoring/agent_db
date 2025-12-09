#!/usr/bin/env python3

from cmk.graphing.v1 import Title
from cmk.graphing.v1.metrics import (
    Metric,
    Unit,
    Color,
    StrictPrecision,
    DecimalNotation,
)


def _create_metric(statement_name):
    return Metric(
        name=f"query_runtime_{statement_name}",
        title=Title(f"Query Runtime {statement_name}"),
        unit=Unit(DecimalNotation("s")),
        color=Color.LIGHT_GREEN,
    )

metric_query_runtime_mssql_availability_groups = _create_metric("mssql_availability_groups")
metric_query_runtime_mssql_backup = _create_metric("mssql_backup")
metric_query_runtime_mssql_blocked_sessions = _create_metric("mssql_blocked_sessions")
metric_query_runtime_mssql_connections = _create_metric("mssql_connections")
metric_query_runtime_mssql_counters = _create_metric("mssql_counters")
metric_query_runtime_mssql_databases = _create_metric("mssql_databases")
metric_query_runtime_mssql_datafiles = _create_metric("mssql_datafiles")
metric_query_runtime_mssql_instance = _create_metric("mssql_instance")
metric_query_runtime_mssql_jobs = _create_metric("mssql_jobs")
metric_query_runtime_mssql_maxservermem = _create_metric("mssql_maxservermem")
metric_query_runtime_mssql_mirroring = _create_metric("mssql_mirroring")
metric_query_runtime_mssql_tablespaces = _create_metric("mssql_tablespaces")
metric_query_runtime_mssql_transactionlogs = _create_metric("mssql_transactionlogs")
metric_query_runtime_mssql_version = _create_metric("mssql_version")
metric_query_runtime_mysql_capacity = _create_metric("mysql_capacity")
metric_query_runtime_mysql_global = _create_metric("mysql_global")
metric_query_runtime_mysql_slaves = _create_metric("mysql_slaves")
metric_query_runtime_mysql_threads_connected = _create_metric("mysql_threads_connected")
metric_query_runtime_oracle_asm_diskgroup = _create_metric("oracle_asm_diskgroup")
metric_query_runtime_oracle_custom_statement = _create_metric("oracle_custom_statement")
metric_query_runtime_oracle_dataguard_stats = _create_metric("oracle_dataguard_stats")
metric_query_runtime_oracle_instance = _create_metric("oracle_instance")
metric_query_runtime_oracle_jobs = _create_metric("oracle_jobs")
metric_query_runtime_oracle_locks = _create_metric("oracle_locks")
metric_query_runtime_oracle_logswitches = _create_metric("oracle_logswitches")
metric_query_runtime_oracle_longactivesessions = _create_metric("oracle_longactivesessions")
metric_query_runtime_oracle_longterm_statement = _create_metric("oracle_longterm_statement")
metric_query_runtime_oracle_performance = _create_metric("oracle_performance")
metric_query_runtime_oracle_processes = _create_metric("oracle_processes")
metric_query_runtime_oracle_recovery_area = _create_metric("oracle_recovery_area")
metric_query_runtime_oracle_recovery_status = _create_metric("oracle_recovery_status")
metric_query_runtime_oracle_rman = _create_metric("oracle_rman")
metric_query_runtime_oracle_sessions = _create_metric("oracle_sessions")
metric_query_runtime_oracle_systemparameter = _create_metric("oracle_systemparameter")
metric_query_runtime_oracle_tablespaces = _create_metric("oracle_tablespaces")
metric_query_runtime_oracle_undostat = _create_metric("oracle_undostat")
metric_query_runtime_oracle_version = _create_metric("oracle_version")
metric_query_runtime_postgres_bloat = _create_metric("postgres_bloat")
metric_query_runtime_postgres_connections = _create_metric("postgres_connections")
metric_query_runtime_postgres_cache_hitratio = _create_metric("postgres_cache_hitratio")
metric_query_runtime_postgres_locks = _create_metric("postgres_locks")
metric_query_runtime_postgres_query_duration = _create_metric("postgres_query_duration")
metric_query_runtime_postgres_sessions = _create_metric("postgres_sessions")
metric_query_runtime_postgres_stat_database = _create_metric("postgres_stat_database")
metric_query_runtime_postgres_stats = _create_metric("postgres_stats")
metric_query_runtime_postgres_txn_wraparound = _create_metric("postgres_txn_wraparound")
metric_query_runtime_postgres_version = _create_metric("postgres_version")
