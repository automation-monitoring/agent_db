SELECT upper(i.instance_name)
       ||'|'|| d.DB_UNIQUE_NAME
       ||'|'|| d.DATABASE_ROLE
       ||'|'|| d.open_mode
       ||'|'|| dh.file#
       ||'|'|| round((dh.CHECKPOINT_TIME-to_date('01.01.1970','dd.mm.yyyy'))*24*60*60)
       ||'|'|| round((sysdate-dh.CHECKPOINT_TIME)*24*60*60)
       ||'|'|| dh.STATUS
       ||'|'|| dh.RECOVER
       ||'|'|| dh.FUZZY
       ||'|'|| dh.CHECKPOINT_CHANGE#
       ||'|'|| nvl(vb.STATUS, 'unknown')
       ||'|'|| nvl2(vb.TIME, round((sysdate-vb.TIME)*24*60*60), 0)
FROM V$datafile_header dh
JOIN v$database d on 1=1
JOIN v$instance i on 1=1
LEFT OUTER JOIN v$backup vb on vb.file# = dh.file#
LEFT OUTER JOIN V$PDBS vp on dh.con_id = vp.con_id
ORDER BY dh.file#;