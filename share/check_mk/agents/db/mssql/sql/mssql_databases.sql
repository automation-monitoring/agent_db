SELECT name,
  DATABASEPROPERTYEX(name, 'Status') AS Status,
  DATABASEPROPERTYEX(name, 'Recovery') AS Recovery,
  DATABASEPROPERTYEX(name, 'IsAutoClose') AS auto_close,
  DATABASEPROPERTYEX(name, 'IsAutoShrink') AS auto_shrink
FROM sys.databases;
