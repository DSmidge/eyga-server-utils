-- Commands for converting InnoDB to MyISAM engine in tables
select concat("ALTER TABLE ", t.TABLE_SCHEMA, ".", t.TABLE_NAME," ENGINE=MyISAM;") AS ExecuteTheString
from information_schema.`TABLES` t
where t.TABLE_TYPE = 'BASE TABLE'
and t.TABLE_SCHEMA not in ('mysql', 'information_schema', 'performance_schema')
and t.ENGINE = 'InnoDB';

-- Commands for converting all table collations to utf8_general_ci (change to your default)
select t.TABLE_COLLATION, concat("ALTER TABLE ", t.TABLE_SCHEMA, ".", t.TABLE_NAME," COLLATE utf8_general_ci;") AS ExecuteTheString
from information_schema.`TABLES` t
where t.TABLE_TYPE = 'BASE TABLE'
and t.TABLE_SCHEMA not in ('mysql', 'information_schema', 'performance_schema')
and t.TABLE_COLLATION not in ('utf8_general_ci', 'utf8_bin');

-- Commands for converting all column collations to utf8_general_ci (change to your default)
select c.COLLATION_NAME, concat("ALTER TABLE ", t.TABLE_SCHEMA, ".", t.TABLE_NAME, " ALTER COLUMN ", c.COLUMN_NAME, ";") as ExecuteTheString
from information_schema.`TABLES` t
join information_schema.`COLUMNS` c on c.TABLE_CATALOG = t.TABLE_CATALOG and c.TABLE_SCHEMA = t.TABLE_SCHEMA and c.TABLE_NAME = t.TABLE_NAME
where t.TABLE_TYPE = 'BASE TABLE'
and t.TABLE_SCHEMA not in ('mysql', 'information_schema', 'performance_schema')
and c.COLLATION_NAME not in ('utf8_general_ci', 'utf8_bin');
