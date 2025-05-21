SELECT upper(d.NAME)
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
FROM  V$datafile_header dh, v$database d, v$instance i
ORDER BY dh.file#;
