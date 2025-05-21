SELECT datname, datid, usename, client_addr, '' AS state,
  COALESCE(ROUND(EXTRACT(epoch FROM now()-query_start))::int,0)
  AS seconds, procpid as pid,
  query AS current_query FROM pg_stat_activity
  WHERE (query_start IS NOT NULL AND
  current_query NOT LIKE '<IDLE>%')
  ORDER BY query_start, procpid DESC;