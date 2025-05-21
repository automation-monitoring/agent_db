select upper(i.instance_name)
	  || '|' || logswitches
from v$instance i ,
	(select count(1) logswitches
	 from v$loghist h , v$instance i
	 where h.first_time > sysdate - 1/24
	 and h.thread# = i.instance_number
	);
