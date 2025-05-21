DECLARE @HADRStatus sql_variant;
DECLARE @SQLCommand nvarchar(max);

-- Check if Always On Availability Groups (AG) is enabled
SET @HADRStatus = (SELECT SERVERPROPERTY('IsHadrEnabled'));

IF (@HADRStatus IS NULL OR @HADRStatus <> 1)
BEGIN
    -- Run query when Always On AG is not enabled
    SET @SQLCommand = '
        SELECT
            sys.databases.name AS database_name,
            CONVERT(VARCHAR, DATEADD(s, MAX(DATEDIFF(s, ''19700101'', backup_finish_date)
            - (CASE WHEN time_zone IS NOT NULL AND time_zone <> 127 THEN 60 * 15 * time_zone ELSE 0 END)), ''19700101''), 120) AS last_backup_date,
            machine_name,
            ''True'' AS is_primary_replica,
            ''1'' AS is_local,
            '''' AS replica_id,
            type
        FROM
            msdb.dbo.backupset
            LEFT OUTER JOIN sys.databases ON sys.databases.name = msdb.dbo.backupset.database_name
        WHERE
            UPPER(machine_name) = UPPER(CAST(SERVERPROPERTY(''Machinename'') AS VARCHAR))
        GROUP BY
            type,
            machine_name,
            sys.databases.name;
    ';
END
ELSE
BEGIN
    -- Run query when Always On AG is enabled
    SET @SQLCommand = '
        SELECT
            db.name AS database_name,
            CONVERT(VARCHAR, DATEADD(s, MAX(DATEDIFF(s, ''19700101'', b.backup_finish_date)
            - (CASE WHEN time_zone IS NOT NULL AND time_zone <> 127 THEN 60 * 15 * time_zone ELSE 0 END)), ''19700101''), 120) AS last_backup_date,
            b.machine_name,
            ISNULL(rep.is_primary_replica, 0) AS is_primary_replica,
            rep.is_local,
            ISNULL(CONVERT(VARCHAR(40), rep.replica_id), '''') AS replica_id,
            b.type
        FROM
            msdb.dbo.backupset b
            LEFT OUTER JOIN sys.databases db ON b.database_name = db.name
            LEFT OUTER JOIN sys.dm_hadr_database_replica_states rep ON db.database_id = rep.database_id
        WHERE
            (rep.is_local IS NULL OR rep.is_local = 1)
            AND (rep.is_primary_replica IS NULL OR rep.is_primary_replica = ''True'')
            AND UPPER(b.machine_name) = UPPER(CAST(SERVERPROPERTY(''Machinename'') AS VARCHAR))
        GROUP BY
            b.type,
            rep.replica_id,
            rep.is_primary_replica,
            rep.is_local,
            db.name,
            b.machine_name,
            rep.synchronization_state,
            rep.synchronization_health;
    ';
END

EXEC (@SQLCommand);
