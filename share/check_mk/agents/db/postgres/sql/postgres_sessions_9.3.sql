SELECT state = 'idle', count(*) FROM pg_stat_activity
  WHERE state IS NOT NULL
  GROUP BY (state = 'idle');
