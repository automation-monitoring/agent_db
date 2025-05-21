select decode(vp.con_id, null, upper(i.INSTANCE_NAME)
                 ,upper(i.INSTANCE_NAME || '.' || vp.name))
       ||'|'|| ACTIVEBLKS
       ||'|'|| MAXCONCURRENCY
       ||'|'|| TUNED_UNDORETENTION
       ||'|'|| maxquerylen
       ||'|'|| NOSPACEERRCNT
from v$instance i
join
    (select * from v$undostat
      where TUNED_UNDORETENTION > 0
     order by end_time desc
     fetch next 1 rows only
    ) u on 1=1
left outer join v$pdbs vp on vp.con_id = u.con_id;