SELECT 
    upper(vp.name)
    || '|' || s.sid
    || '|' || s.serial#
    || '|' || s.machine
    || '|' || s.process
    || '|' || s.osuser
    || '|' || s.program
    || '|' || s.last_call_et
    || '|' || s.sql_id
FROM 
    v$session s
JOIN (
    SELECT 
        vp.con_id
        , i.instance_name || '.' || vp.name name
    FROM 
        v$containers vp
    JOIN 
        v$instance i ON 1 = 1
    JOIN 
        v$database d ON 1=1
    WHERE 
        d.cdb = 'YES' AND vp.con_id <> 2
    UNION ALL
    SELECT 
        0
        , instance_name
    FROM 
        v$instance
) vp ON 1=1
WHERE 
    s.status = 'ACTIVE'
    AND s.type != 'BACKGROUND'
    AND s.username IS NOT NULL
    AND s.username NOT IN ('PUBLIC')
    AND s.last_call_et > 60*60

UNION ALL

SELECT 
    upper(i.instance_name || '.' || vp.name)
    || '||||||||'
FROM 
    v$containers vp
JOIN 
    v$instance i ON 1 = 1
JOIN 
    v$database d ON 1=1
WHERE 
    d.cdb = 'YES' AND vp.con_id <> 2

UNION ALL

SELECT 
    upper(i.instance_name)
    || '||||||||'
FROM 
    v$instance i;
