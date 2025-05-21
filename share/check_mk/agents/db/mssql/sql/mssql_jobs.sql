SELECT
    sj.job_id,
    sj.name AS job_name,
    sj.enabled AS job_enabled,
    CAST(sjs.next_run_date AS VARCHAR(8)) AS next_run_date,
    CAST(sjs.next_run_time AS VARCHAR(6)) AS next_run_time,
    sjserver.last_run_outcome,
    sjserver.last_outcome_message,
    CAST(sjserver.last_run_date AS VARCHAR(8)) AS last_run_date,
    CAST(sjserver.last_run_time AS VARCHAR(6)) AS last_run_time,
    sjserver.last_run_duration,
    ss.enabled AS schedule_enabled,
    CONVERT(VARCHAR, CURRENT_TIMESTAMP, 20) AS server_current_time
FROM
    dbo.sysjobs sj
LEFT JOIN
    dbo.sysjobschedules sjs ON sj.job_id = sjs.job_id
LEFT JOIN
    dbo.sysjobservers sjserver ON sj.job_id = sjserver.job_id
LEFT JOIN
    dbo.sysschedules ss ON sjs.schedule_id = ss.schedule_id
ORDER BY
    sj.name,
    sjs.next_run_date ASC,
    sjs.next_run_time ASC;