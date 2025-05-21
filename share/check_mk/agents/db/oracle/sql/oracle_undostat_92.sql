select upper(i.INSTANCE_NAME)
           ||'|-1'
           ||'|'|| MAXCONCURRENCY
           ||'|-1'
           ||'|'|| maxquerylen
           ||'|'|| NOSPACEERRCNT
        from v$instance i,
        (select * from (select *
                        from v$undostat order by end_time desc
                       )
                  where rownum = 1
        );