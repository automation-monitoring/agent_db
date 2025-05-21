select upper(i.INSTANCE_NAME)
           ||'|'|| ACTIVEBLKS
           ||'|'|| MAXCONCURRENCY
           ||'|'|| TUNED_UNDORETENTION
           ||'|'|| maxquerylen
           ||'|'|| NOSPACEERRCNT
from v$instance i,
    (select * from (select *
                    from v$undostat order by end_time desc
                   )
              where rownum = 1
                and TUNED_UNDORETENTION > 0
    );
