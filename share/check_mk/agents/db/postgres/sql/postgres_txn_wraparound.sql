-- This query has been stolen from check_postgres (https://bucardo.org/check_postgres/)
SELECT datname, age(datfrozenxid)
  AS age FROM pg_database
  WHERE datallowconn
  ORDER BY 1, 2
