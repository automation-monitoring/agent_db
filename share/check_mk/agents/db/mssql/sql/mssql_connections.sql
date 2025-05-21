SELECT name AS DBName, ISNULL((SELECT  COUNT(dbid) AS NumberOfConnections FROM 
    sys.sysprocesses WHERE dbid > 0 AND name = DB_NAME(dbid) GROUP BY dbid ),0) AS NumberOfConnections
    FROM
        sys.databases