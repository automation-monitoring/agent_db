SELECT /* check_mk rman1 */ upper(name)
       || '|'|| 'COMPLETED'
       || '|'|| to_char(COMPLETION_TIME, 'YYYY-mm-dd_HH24:MI:SS')
       || '|'|| to_char(COMPLETION_TIME, 'YYYY-mm-dd_HH24:MI:SS')
       || '|'|| CASE WHEN INCREMENTAL_LEVEL IS NULL THEN 'DB_FULL' ELSE 'DB_INCR' END
       || '|'|| INCREMENTAL_LEVEL
       || '|'|| ROUND(((sysdate-COMPLETION_TIME) * 24 * 60), 0)
       || '|'|| INCREMENTAL_CHANGE#
FROM (
    SELECT UPPER(i.instance_name) name
         , bd2.INCREMENTAL_LEVEL
         , bd2.INCREMENTAL_CHANGE#
         , MIN(bd2.COMPLETION_TIME) COMPLETION_TIME
    FROM (
		SELECT bd.file#
             , bd.INCREMENTAL_LEVEL
             , bd.COMPLETION_TIME COMPLETION_TIME
		FROM
		   (SELECT file#
				 , INCREMENTAL_LEVEL
				 , MAX(COMPLETION_TIME) COMPLETION_TIME
			FROM v$backup_datafile 
			GROUP BY file#,INCREMENTAL_LEVEL) bd
        JOIN v$datafile_header dh ON dh.file# = bd.file#
        WHERE dh.status = 'ONLINE'
             AND dh.con_id <> 2
    ) bd
    JOIN v$backup_datafile bd2 ON bd2.file# = bd.file#
                              AND bd2.COMPLETION_TIME = bd.COMPLETION_TIME
    JOIN v$database vd ON vd.RESETLOGS_CHANGE# = bd2.RESETLOGS_CHANGE#
    JOIN v$instance i ON 1=1
    GROUP BY UPPER(i.instance_name), bd2.INCREMENTAL_LEVEL, bd2.INCREMENTAL_CHANGE#
)

UNION ALL

SELECT /* check_mk rman2 */ name
       || '|' || 'COMPLETED'
       || '|'
       || '|' || to_char(CHECKPOINT_TIME, 'yyyy-mm-dd_hh24:mi:ss')
       || '|' || 'CONTROLFILE'
       || '|'
       || '|' || ROUND((sysdate - CHECKPOINT_TIME) * 24 * 60)
       || '|' || '0'
FROM (
    SELECT UPPER(i.instance_name) name
         , MAX(bcd.CHECKPOINT_TIME) CHECKPOINT_TIME
    FROM v$database d
    JOIN V$BACKUP_CONTROLFILE_DETAILS bcd ON d.RESETLOGS_CHANGE# = bcd.RESETLOGS_CHANGE#
    JOIN v$instance i ON 1=1
    GROUP BY UPPER(i.instance_name)
)

UNION ALL

SELECT /* check_mk rman3 */ name
       || '|COMPLETED'
       || '|'|| to_char(sysdate, 'YYYY-mm-dd_HH24:MI:SS')
       || '|'|| to_char(completed, 'YYYY-mm-dd_HH24:MI:SS')
       || '|ARCHIVELOG||'
       || ROUND((sysdate - completed) * 24 * 60, 0)
       || '|'
FROM (
    SELECT UPPER(i.instance_name) name
         , MAX(a.completion_time) completed
         , CASE WHEN a.backup_count > 0 THEN 1 ELSE 0 END
    FROM v$archived_log a, v$database d, v$instance i
    WHERE a.backup_count > 0
      AND a.dest_id IN (
        SELECT b.dest_id
        FROM v$archive_dest b
        WHERE b.target = 'PRIMARY'
          AND b.SCHEDULE = 'ACTIVE'
      )
    GROUP BY d.NAME, i.instance_name, CASE WHEN a.backup_count > 0 THEN 1 ELSE 0 END
);
