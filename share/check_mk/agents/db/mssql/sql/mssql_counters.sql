SELECT 
    CONCAT(
        RTRIM(LTRIM(object_name)), '|',
        RTRIM(LTRIM(counter_name)), '|',
        RTRIM(LTRIM(instance_name)), '|',
        RTRIM(LTRIM(CAST(cntr_value AS VARCHAR)))
    ) AS concatenated_columns
FROM 
    sys.dm_os_performance_counters
WHERE 
    object_name NOT LIKE '%Deprecated%'
