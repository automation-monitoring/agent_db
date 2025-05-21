SELECT datname, datid, usename, client_addr, state AS state,
  COALESCE(ROUND(EXTRACT(epoch FROM now()-query_start))::int,0)
  AS seconds, pid,
  query AS current_query FROM pg_stat_activity
  WHERE (query_start IS NOT NULL AND
  (state NOT LIKE 'idle%' OR state IS NULL))
  ORDER BY query_start, pid DESC;