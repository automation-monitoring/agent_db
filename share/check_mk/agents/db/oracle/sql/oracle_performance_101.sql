SELECT 
    upper(i.INSTANCE_NAME) || '|' || 'sys_time_model' || '|' || S.STAT_NAME || '|' || ROUND(s.value/1000000) AS result
FROM 
    v$instance i
JOIN 
    v$sys_time_model s 
    ON s.stat_name IN ('DB time', 'DB CPU')

UNION

SELECT 
    upper(i.INSTANCE_NAME) || '|' || 'buffer_pool_statistics' || '|' || b.name || '|' || b.db_block_gets || '|' || b.db_block_change || '|' || b.consistent_gets || '|' || b.physical_reads || '|' || b.physical_writes || '|' || b.FREE_BUFFER_WAIT || '|' || b.BUFFER_BUSY_WAIT AS result
FROM 
    v$instance i, 
    v$BUFFER_POOL_STATISTICS b

UNION

SELECT 
    upper(i.INSTANCE_NAME) || '|' || 'SGA_info' || '|' || s.name || '|' || s.bytes AS result
FROM 
    v$sgainfo s, 
    v$instance i

UNION

SELECT 
    upper(i.INSTANCE_NAME) || '|' || 'librarycache' || '|' || b.namespace || '|' || b.gets || '|' || b.gethits || '|' || b.pins || '|' || b.pinhits || '|' || b.reloads || '|' || b.invalidations AS result
FROM 
    v$instance i, 
    v$librarycache b
