select upper(i.instance_name)
	 || '|' || s.sid
	 || '|' || s.serial#
	 || '|' || s.machine
	 || '|' || s.process
	 || '|' || s.osuser
	 || '|' || s.program
	 || '|' || s.last_call_et
	 || '|' || s.sql_id
from v$session s, v$instance i
where s.status = 'ACTIVE'
and type != 'BACKGROUND'
and s.username is not null
and s.username not in('PUBLIC')
and s.last_call_et > 60*60
union all
select upper(i.instance_name)
	 || '||||||||'
from v$instance i;
