select upper(i.instance_name)
     || '|' || CURRENT_UTILIZATION
     || '|' || ltrim(rtrim(LIMIT_VALUE))
from v$resource_limit, v$instance i
where RESOURCE_NAME = 'processes';