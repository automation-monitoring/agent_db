select g.STATE
           || '|' || TYPE
           || '|' || 'N'
           || '|' || sector_size
           || '|' || block_size
           || '|' || allocation_unit_size
           || '|' || total_mb
           || '|' || free_mb
           || '|' || required_mirror_free_mb
           || '|' || usable_file_mb
           || '|' || offline_disks
           || '|' || 'N'
           || '|' || name || '/'
from v$asm_diskgroup;
