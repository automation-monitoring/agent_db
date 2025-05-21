SELECT datname, granted, mode
  FROM pg_locks l
  RIGHT JOIN pg_database d ON (d.oid=l.database)
  WHERE d.datallowconn;
