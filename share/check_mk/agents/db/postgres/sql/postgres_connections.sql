SELECT datname,
  (SELECT setting AS mc FROM pg_settings WHERE name = 'max_connections') AS mc,
  COUNT(state) FILTER (WHERE state='idle') AS idle,
  COUNT(state) FILTER (WHERE state='active') AS active
FROM pg_stat_activity group by 1;
