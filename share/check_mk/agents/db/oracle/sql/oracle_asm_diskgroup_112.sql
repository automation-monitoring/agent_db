select g.STATE
     || '|' || g.type
     || '|' || g.name
     || '|' || g.BLOCK_SIZE
     || '|' || g.ALLOCATION_UNIT_SIZE
     || '|' || g.REQUIRED_MIRROR_FREE_MB
     || '|' || sum(d.total_mb)
     || '|' || sum(d.free_mb)
     || '|' || d.failgroup
     || '|' || max(d.VOTING_FILE)
     || '|' || d.FAILGROUP_TYPE
     || '|' || g.offline_disks
     || '|' || min(decode(d.REPAIR_TIMER, 0, 8640000, d.REPAIR_TIMER))
     || '|' || count(*)
FROM v$asm_diskgroup g
LEFT OUTER JOIN v$asm_disk d on d.group_number = g.group_number
     and d.group_number = g.group_number
     and d.group_number <> 0
GROUP BY g.name
     , g.state
     , g.type
     , d.failgroup
     , d.VOTING_FILE
     , g.BLOCK_SIZE
     , g.ALLOCATION_UNIT_SIZE
     , g.REQUIRED_MIRROR_FREE_MB
     , g.offline_disks
     , d.FAILGROUP_TYPE
     , d.REPAIR_TIMER
ORDER BY g.name, d.failgroup;
