SELECT
  GroupsName.name,
  Groups.primary_replica,
  Groups.synchronization_health,
  Groups.synchronization_health_desc,
  Groups.primary_recovery_health_desc
FROM sys.dm_hadr_availability_group_states Groups
INNER JOIN master.sys.availability_groups GroupsName
ON Groups.group_id = GroupsName.group_id