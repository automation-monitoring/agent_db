select upper(i.instance_name)
	 || '|' || NAME
	 || '|' || DISPLAY_VALUE
	 || '|' || ISDEFAULT
from v$system_parameter, v$instance i
where name not like '!_%' ESCAPE '!';
