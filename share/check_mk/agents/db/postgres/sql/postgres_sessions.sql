SELECT current_query = '<IDLE>', count(*) FROM pg_stat_activity
  WHERE current_query IS NOT NULL
  GROUP BY (current_query = '<IDLE>');
