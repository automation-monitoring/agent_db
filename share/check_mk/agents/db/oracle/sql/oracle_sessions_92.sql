          select upper(i.instance_name)
               || '|' || CURRENT_UTILIZATION
               || '|' || ltrim(LIMIT_VALUE)
               || '|' || MAX_UTILIZATION
          from v$resource_limit, v$instance i
          where RESOURCE_NAME = 'sessions';
