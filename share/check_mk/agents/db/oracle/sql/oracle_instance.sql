select upper(i.instance_name)
		 || '|' || i.VERSION
		 || '|' || i.STATUS
		 || '|' || i.LOGINS
		 || '|' || i.ARCHIVER
		 || '|' || round((sysdate - i.startup_time) * 24*60*60)
		 || '|' || DBID
		 || '|' || LOG_MODE
		 || '|' || DATABASE_ROLE
		 || '|' || FORCE_LOGGING
		 || '|' || d.name
		 || '|' || to_char(d.created, 'ddmmyyyyhh24mi')
from v$instance i, v$database d;
