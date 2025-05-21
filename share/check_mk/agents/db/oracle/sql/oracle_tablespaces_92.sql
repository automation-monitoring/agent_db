select upper(i.instance_name)
       || '|' || file_name ||'|'|| tablespace_name ||'|'|| fstatus ||'|'|| AUTOEXTENSIBLE
       ||'|'|| blocks ||'|'|| maxblocks ||'|'|| USER_BLOCKS ||'|'|| INCREMENT_BY
       ||'|'|| ONLINE_STATUS ||'|'|| BLOCK_SIZE
       ||'|'|| decode(tstatus,'READ ONLY', 'READONLY', tstatus) || '|' || free_blocks
       ||'|'|| contents
       ||'|'|| iversion
from v$database d , v$instance i, (
         select f.file_name, f.tablespace_name, f.status fstatus, f.AUTOEXTENSIBLE,
         f.blocks, f.maxblocks, f.USER_BLOCKS, f.INCREMENT_BY,
         f.ONLINE_STATUS, t.BLOCK_SIZE, t.status tstatus, nvl(sum(fs.blocks),0) free_blocks, t.contents,
         (select version from v$instance) iversion
         from dba_data_files f, dba_tablespaces t, dba_free_space fs
         where f.tablespace_name = t.tablespace_name
         and f.file_id = fs.file_id(+)
         group by f.file_name, f.tablespace_name, f.status, f.autoextensible,
         f.blocks, f.maxblocks, f.user_blocks, f.increment_by, f.online_status,
         t.block_size, t.status, t.contents
         UNION
         select f.file_name, f.tablespace_name, f.status, f.AUTOEXTENSIBLE,
         f.blocks, f.maxblocks, f.USER_BLOCKS, f.INCREMENT_BY, 'TEMP',
         t.BLOCK_SIZE, t.status, sum(sh.blocks_free) free_blocks, 'TEMPORARY',
         (select version from v$instance) version
         from v$thread th, dba_temp_files f, dba_tablespaces t, v$temp_space_header sh
         WHERE f.tablespace_name = t.tablespace_name and f.file_id = sh.file_id
         GROUP BY th.instance, f.file_name, f.tablespace_name, f.status,
         f.autoextensible, f.blocks, f.maxblocks, f.user_blocks, f.increment_by,
         'TEMP', t.block_size, t.status)
where d.database_role = 'PRIMARY'
