select upper(instance_name)
	|| '|' || version_full
	|| '|' || status
	|| '|' || logins
	|| '|' || archiver
	|| '|' || round((sysdate - startup_time) * 24*60*60)
	|| '|' || dbid
	|| '|' || log_mode
	|| '|' || database_role
	|| '|' || force_logging
	|| '|' || name
	|| '|' || to_char(created, 'ddmmyyyyhh24mi')
	|| '|' || upper(value)
	|| '|' || con_id
	|| '|' || pname
	|| '|' || pdbid
	|| '|' || popen_mode
	|| '|' || prestricted
	|| '|' || ptotal_time
	|| '|' || precovery_status
	|| '|' || round(nvl(popen_time, -1))
	|| '|' || pblock_size
from(
	select i.instance_name, i.version_full, i.status, i.logins, i.archiver
		 ,i.startup_time, d.dbid, d.log_mode, d.database_role, d.force_logging
		 ,d.name, d.created, p.value, vp.con_id, vp.name pname
		 ,vp.dbid pdbid, vp.open_mode popen_mode, vp.restricted prestricted, vp.total_size ptotal_time
		 ,vp.block_size pblock_size, vp.recovery_status precovery_status
		 ,(cast(systimestamp as date) - cast(open_time as date))  * 24*60*60 popen_time
	from v$instance i
	join v$database d on 1=1
	join v$parameter p on 1=1
	join v$pdbs vp on 1=1
	where p.name = 'enable_pluggable_database'
	union all
	select
		 i.instance_name, i.version_full, i.status, i.logins, i.archiver
		 ,i.startup_time, d.dbid, d.log_mode, d.database_role, d.force_logging
		 ,d.name, d.created, p.value, 0 con_id, null pname
		 ,0 pdbis, null popen_mode, null prestricted, null ptotal_time
		 ,0 pblock_size, null precovery_status, null popen_time
	from v$instance i
	join v$database d on 1=1
	join v$parameter p on 1=1
	where p.name = 'enable_pluggable_database'
	order by con_id
);
