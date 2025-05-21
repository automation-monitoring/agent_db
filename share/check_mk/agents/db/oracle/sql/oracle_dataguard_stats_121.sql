SELECT upper(i.instance_name)
       ||'|'|| upper(d.DB_UNIQUE_NAME)
       ||'|'|| d.DATABASE_ROLE
       ||'|'|| ds.name
       ||'|'|| ds.value
       ||'|'|| d.SWITCHOVER_STATUS
       ||'|'|| d.DATAGUARD_BROKER
       ||'|'|| d.PROTECTION_MODE
       ||'|'|| d.FS_FAILOVER_STATUS
       ||'|'|| d.FS_FAILOVER_OBSERVER_PRESENT
       ||'|'|| d.FS_FAILOVER_OBSERVER_HOST
       ||'|'|| d.FS_FAILOVER_CURRENT_TARGET
       ||'|'|| ms.status
FROM v$database d
JOIN v$parameter vp on 1=1
JOIN v$instance i on 1=1
left outer join V$dataguard_stats ds on 1=1
left outer join v$managed_standby ms on ms.process = 'MRP0'
WHERE vp.name = 'log_archive_config'
AND   vp.value is not null
ORDER BY 1;