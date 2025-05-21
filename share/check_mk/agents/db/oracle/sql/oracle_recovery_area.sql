select upper(i.instance_name)
       ||'|'|| round((SPACE_USED-SPACE_RECLAIMABLE)/
                 (CASE NVL(SPACE_LIMIT,1) WHEN 0 THEN 1 ELSE SPACE_LIMIT END)*100)
       ||'|'|| round(SPACE_LIMIT/1024/1024)
       ||'|'|| round(SPACE_USED/1024/1024)
       ||'|'|| round(SPACE_RECLAIMABLE/1024/1024)
       ||'|'|| d.FLASHBACK_ON
from V$RECOVERY_FILE_DEST, v$database d, v$instance i;