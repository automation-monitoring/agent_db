DECLARE
    TYPE x IS TABLE OF VARCHAR2(20000) INDEX BY PLS_INTEGER;
    xx x;
BEGIN
  BEGIN
	  EXECUTE IMMEDIATE 'SELECT upper(vp.name)
	 ||''|''|| j.OWNER
	 ||''|''|| j.JOB_NAME
	 ||''|''|| j.STATE
	 ||''|''|| ROUND((TRUNC(sysdate) + j.LAST_RUN_DURATION - TRUNC(sysdate)) * 86400)
	 ||''|''|| j.RUN_COUNT
	 ||''|''|| j.ENABLED
	 ||''|''|| NVL(j.NEXT_RUN_DATE, to_date(''1970-01-01'', ''YYYY-mm-dd''))
	 ||''|''|| NVL(j.SCHEDULE_NAME, ''-'')
	 ||''|''|| jd.STATUS
FROM dba_scheduler_jobs j
join v$database vd on 1 = 1
join v$instance i on 1 = 1
left outer join (SELECT owner, job_name, max(LOG_ID) log_id
						FROM dba_scheduler_job_run_details dd
						group by owner, job_name
			  ) jm on  jm.JOB_NAME = j.JOB_NAME
				   and jm.owner=j.OWNER
left outer join dba_scheduler_job_run_details jd
			  on  jd.owner = jm.OWNER
			  AND jd.JOB_NAME = jm.JOB_NAME
			  AND jd.LOG_ID = jm.LOG_ID
WHERE vd.database_role = ''PRIMARY''
AND vd.open_mode = ''READ WRITE''
AND not (j.auto_drop = ''TRUE'' and REPEAT_INTERVAL is null)'
	  BULK COLLECT INTO xx;
	  IF xx.COUNT >= 1 THEN
		FOR i IN 1 .. xx.COUNT LOOP
			DBMS_OUTPUT.PUT_LINE(xx(i));
		END LOOP;
      END IF;
    EXCEPTION
        WHEN OTHERS THEN
			FOR cur1 IN (SELECT UPPER(name) name FROM v$database) LOOP
				DBMS_OUTPUT.PUT_LINE(cur1.name || '| Debug (102): ' || SQLERRM);
			END LOOP;
    END;
END;
