SELECT -- system and user tbs
    upper(decode(vp.con_id, null, d.name, 0, d.name, d.name||'.'||vp.name))
    || '|' || dbf.file_name
    || '|' || dbf.tablespace_name
    || '|' || dbf.fstatus
    || '|' || dbf.autoextensible
    || '|' || dbf.blocks
    || '|' || dbf.maxblocks
    || '|' || dbf.user_blocks
    || '|' || dbf.increment_by
    || '|' || dbf.online_status
    || '|' || dbf.block_size
    || '|' || decode(tstatus,'READ ONLY', 'READONLY', tstatus)
    || '|' || dbf.free_blocks
    || '|' || dbf.contents
    || '|' || i.version
FROM v$database d
JOIN v$instance i ON 1=1
JOIN (
    SELECT t.con_id, f.file_name, t.tablespace_name, f.status fstatus, f.autoextensible,
        f.blocks, f.maxblocks, f.user_blocks, f.increment_by,
        f.online_status, t.block_size, t.status tstatus, nvl(sum(fs.blocks),0) free_blocks, t.contents
    FROM cdb_tablespaces t
    JOIN cdb_data_files f ON f.tablespace_name = t.tablespace_name AND f.con_id = t.con_id
    LEFT OUTER JOIN cdb_free_space fs ON f.file_id = fs.file_id AND f.con_id = fs.con_id
    GROUP BY t.con_id, f.file_name, t.tablespace_name, f.status, f.autoextensible,
        f.blocks, f.maxblocks, f.user_blocks, f.increment_by, f.online_status,
        t.block_size, t.status, t.contents
    ) dbf ON 1=1
LEFT OUTER JOIN v$containers vp ON dbf.con_id = vp.con_id
WHERE d.database_role = 'PRIMARY'
UNION
SELECT -- temporary tbs
    upper(decode(vp.con_id, null, d.name, 0, d.name, d.name||'.'||vp.name))
    || '|' || dbf.file_name
    || '|' || dbf.tablespace_name
    || '|' || dbf.fstatus
    || '|' || dbf.autoextensible
    || '|' || dbf.blocks
    || '|' || dbf.maxblocks
    || '|' || dbf.user_blocks
    || '|' || dbf.increment_by
    || '|' || dbf.online_status
    || '|' || dbf.block_size
    || '|' || decode(tstatus,'READ ONLY', 'READONLY', tstatus)
    || '|' || dbf.free_blocks
    || '|' || dbf.contents
    || '|' || i.version
FROM v$database d
JOIN v$instance i ON 1 = 1
JOIN (
    SELECT t.con_id, f.file_name, t.tablespace_name, f.status fstatus, f.autoextensible,
        f.blocks, f.maxblocks, f.user_blocks, f.increment_by,
        'ONLINE' online_status, t.block_size, t.status tstatus, f.blocks - nvl(SUM(tu.blocks),0) free_blocks, t.contents
    FROM cdb_tablespaces t
    LEFT OUTER JOIN cdb_temp_files f ON t.con_id = f.con_id AND t.tablespace_name = f.tablespace_name
    LEFT OUTER JOIN gv$tempseg_usage tu ON f.con_id = tu.con_id AND f.tablespace_name = tu.tablespace AND f.RELATIVE_FNO = tu.SEGRFNO#
    WHERE t.contents = 'TEMPORARY'
    GROUP BY t.con_id, f.file_name, t.tablespace_name, f.status, f.autoextensible,
        f.blocks, f.maxblocks, f.user_blocks, f.increment_by,
        t.block_size, t.status, t.contents
    ) dbf ON 1 = 1
LEFT OUTER JOIN v$containers vp ON dbf.con_id = vp.con_id
WHERE d.database_role = 'PRIMARY'
