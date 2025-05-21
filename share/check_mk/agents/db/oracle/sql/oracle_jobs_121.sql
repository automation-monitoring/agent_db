DECLARE
    TYPE x IS TABLE OF VARCHAR2(20000) INDEX BY PLS_INTEGER;
    xx x;
BEGIN
    BEGIN
        EXECUTE IMMEDIATE
            'SELECT upper(vp.name)
                 ||''|''|| j.OWNER
                 ||''|''|| j.JOB_NAME
                 ||''|''|| j.STATE
                 ||''|''|| ROUND((TRUNC(sysdate) + j.LAST_RUN_DURATION - TRUNC(sysdate)) * 86400)
                 ||''|''|| j.RUN_COUNT
                 ||''|''|| j.ENABLED
                 ||''|''|| NVL(j.NEXT_RUN_DATE, TO_DATE(''1970-01-01'', ''YYYY-mm-dd''))
                 ||''|''|| NVL(j.SCHEDULE_NAME, ''-'')
                 ||''|''|| jd.STATUS
            FROM cdb_scheduler_jobs j
            JOIN (
                SELECT vp.con_id, d.name || ''|'' || vp.name name
                FROM v$containers vp
                JOIN v$database d ON 1=1
                WHERE d.cdb = ''YES'' AND vp.con_id <> 2
                AND d.database_role = ''PRIMARY''
                AND d.open_mode = ''READ WRITE''
                UNION ALL
                SELECT 0, name
                FROM v$database d
                WHERE d.database_role = ''PRIMARY''
                AND d.open_mode = ''READ WRITE''
            ) vp ON j.con_id = vp.con_id
            LEFT OUTER JOIN (
                SELECT con_id, owner, job_name, MAX(LOG_ID) log_id
                FROM cdb_scheduler_job_run_details dd
                GROUP BY con_id, owner, job_name
            ) jm ON jm.JOB_NAME = j.JOB_NAME
            AND jm.owner = j.OWNER
            AND jm.con_id = j.con_id
            LEFT OUTER JOIN cdb_scheduler_job_run_details jd
            ON jd.con_id = jm.con_id
            AND jd.owner = jm.OWNER
            AND jd.JOB_NAME = jm.JOB_NAME
            AND jd.LOG_ID = jm.LOG_ID
            WHERE NOT (j.auto_drop = ''TRUE'' AND REPEAT_INTERVAL IS NULL)'
            BULK COLLECT INTO xx;
            
        IF xx.COUNT >= 1 THEN
            FOR i IN 1 .. xx.COUNT LOOP
                DBMS_OUTPUT.PUT_LINE(xx(i));
            END LOOP;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            FOR cur1 IN (SELECT UPPER(name) name FROM v$database) LOOP
                DBMS_OUTPUT.PUT_LINE(cur1.name || '| Debug (121): ' || SQLERRM);
            END LOOP;
    END;
END;
