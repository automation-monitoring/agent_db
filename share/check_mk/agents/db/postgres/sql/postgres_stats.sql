SELECT
  current_database() AS datname, nspname AS sname,
  relname AS tname, CASE WHEN v IS NULL THEN -1
  ELSE round(extract(epoch FROM v))::int END AS vtime,
  CASE WHEN g IS NULL THEN -1 ELSE round(extract(epoch FROM g))::int
  END AS atime FROM (SELECT nspname, relname,
  GREATEST(pg_stat_get_last_vacuum_time(c.oid),
  pg_stat_get_last_autovacuum_time(c.oid)) AS v,
  GREATEST(pg_stat_get_last_analyze_time(c.oid),
  pg_stat_get_last_autoanalyze_time(c.oid)) AS g
  FROM pg_class c, pg_namespace n WHERE relkind = 'r'
  AND n.oid = c.relnamespace AND n.nspname <> 'information_schema'
  ORDER BY 3) AS foo;