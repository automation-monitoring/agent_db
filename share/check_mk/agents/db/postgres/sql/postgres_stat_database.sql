SELECT 
    datid, 
    datname, 
    numbackends, 
    xact_commit, 
    xact_rollback, 
    blks_read, 
    blks_hit, 
    tup_returned, 
    tup_fetched, 
    tup_inserted, 
    tup_updated, 
    tup_deleted, 
    pg_database_size(datname) AS datsize 
FROM 
    pg_stat_database;
