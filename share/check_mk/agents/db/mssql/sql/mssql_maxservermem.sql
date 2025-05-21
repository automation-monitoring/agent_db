-- Get Maximum server memory in (MB)
-- CAST is needed to transform the output byte string like b'\xff\xff\xff\x7f'| to int
SELECT
    CAST(value AS INT) AS value,
    description
FROM
    sys.configurations
WHERE
    name = 'max server memory (MB)';
