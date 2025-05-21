SELECT 
    @@SERVERNAME as server_name, 
    DB_NAME(database_id) AS [database_name], 
    mirroring_state, 
    mirroring_state_desc, 
    mirroring_role, 
    mirroring_role_desc, 
    mirroring_safety_level, 
    mirroring_safety_level_desc, 
    mirroring_partner_name, 
    mirroring_partner_instance, 
    mirroring_witness_name, 
    mirroring_witness_state, 
    mirroring_witness_state_desc
FROM 
    sys.database_mirroring
WHERE 
    mirroring_state IS NOT NULL;
