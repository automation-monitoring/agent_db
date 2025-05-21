-- This query has been stolen from check_postgres (https://bucardo.org/check_postgres/)
SELECT
  round(100.*sd.blks_hit/(sd.blks_read+sd.blks_hit), 2) AS dhitratio,
  d.datname,
  r.rolname AS rolname
  FROM pg_stat_database sd
  JOIN pg_database d ON (d.oid=sd.datid)
  JOIN pg_roles r ON (r.oid=d.datdba)
  WHERE sd.blks_read+sd.blks_hit<>0
