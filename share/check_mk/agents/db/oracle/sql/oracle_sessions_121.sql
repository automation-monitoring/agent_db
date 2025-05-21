SELECT upper(vp.name)
       || '|' || ltrim(COUNT(1))
       || decode(vp.con_id
                 , 0, '|'||ltrim(rtrim(LIMIT_VALUE))||'|-1')
FROM ( SELECT vp.con_id
           ,i.instance_name || '.' || vp.name name
       FROM v$containers vp
       JOIN v$instance i ON 1 = 1
       JOIN v$database d on 1=1
       WHERE d.cdb = 'YES' and vp.con_id <> 2
      UNION ALL
       SELECT 0, instance_name
       FROM v$instance
     ) vp
JOIN v$resource_limit rl on RESOURCE_NAME = 'sessions'
LEFT OUTER JOIN v$session vs ON vp.con_id = vs.con_id
GROUP BY vp.name, vp.con_id, rl.LIMIT_VALUE
ORDER BY 1;
