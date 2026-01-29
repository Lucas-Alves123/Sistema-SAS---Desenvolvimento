import psycopg2
from psycopg2.extras import RealDictCursor
import mysql.connector
import json
from datetime import datetime, date, time

# PostgreSQL Config
PG_CONFIG = {
    "host": "10.24.59.102",
    "database": "sas",
    "user": "sas",
    "password": "Mzffz0n89uWJeSyV",
    "port": "5432"
}

# MySQL Config
MY_CONFIG = {
    "host": "10.24.56.110",
    "database": "sas_sga",
    "user": "sas_sga",
    "password": "tCRkCckF79qAH9LO",
    "port": 3306
}

def get_pg_conn():
    return psycopg2.connect(**PG_CONFIG)

def get_my_conn():
    return mysql.connector.connect(**MY_CONFIG)

def map_type(pg_type, pg_default):
    pg_type = pg_type.lower()
    
    if "nextval" in str(pg_default):
        if "big" in pg_type:
            return "BIGINT AUTO_INCREMENT"
        return "INT AUTO_INCREMENT"
    
    mapping = {
        "integer": "INT",
        "bigint": "BIGINT",
        "character varying": "VARCHAR(255)",
        "character": "CHAR(255)",
        "text": "LONGTEXT",
        "date": "DATE",
        "time without time zone": "TIME",
        "timestamp without time zone": "DATETIME",
        "boolean": "TINYINT(1)",
        "json": "JSON",
        "jsonb": "JSON",
        "bytea": "LONGBLOB"
    }
    
    return mapping.get(pg_type, "VARCHAR(255)")

def migrate():
    pg_conn = get_pg_conn()
    my_conn = get_my_conn()
    pg_cur = pg_conn.cursor(cursor_factory=RealDictCursor)
    my_cur = my_conn.cursor()
    
    # Load schema info
    with open('postgres_schema.json', 'r') as f:
        schema = json.load(f)
    
    # 1. Create Tables
    print("Creating tables in MySQL...")
    
    # Order tables to handle foreign keys (simple approach: usuarios first)
    table_order = ["usuarios", "trabalhadores", "vinculos_trabalhadores", "agendamentos"]
    
    # Disable foreign key checks for creation
    my_cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    for table_name in table_order:
        if table_name not in schema: continue
        
        table_info = schema[table_name]
        columns_def = []
        pk = None
        
        for col in table_info["columns"]:
            name = col["column_name"]
            m_type = map_type(col["data_type"], col["column_default"])
            nullable = "NULL" if col["is_nullable"] == "YES" else "NOT NULL"
            
            # Handle defaults
            default = ""
            if col["column_default"] and "nextval" not in col["column_default"]:
                if "CURRENT_TIMESTAMP" in col["column_default"]:
                    default = "DEFAULT CURRENT_TIMESTAMP"
                elif "::" in col["column_default"]:
                    val = col["column_default"].split("::")[0].strip("'")
                    default = f"DEFAULT '{val}'"
                else:
                    default = f"DEFAULT {col['column_default']}"
            
            columns_def.append(f"`{name}` {m_type} {nullable} {default}")
        
        # Add Primary Key
        for const in table_info["constraints"]:
            if const["constraint_type"] == "PRIMARY KEY":
                pk = const["column_name"]
                break
        
        if pk:
            columns_def.append(f"PRIMARY KEY (`{pk}`)")
            
        create_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n  " + ",\n  ".join(columns_def) + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        
        print(f"Creating table {table_name}...")
        my_cur.execute(f"DROP TABLE IF EXISTS `{table_name}`")
        my_cur.execute(create_query)

    # 2. Add Foreign Keys
    print("Adding foreign keys...")
    for table_name in table_order:
        if table_name not in schema: continue
        table_info = schema[table_name]
        for const in table_info["constraints"]:
            if const["constraint_type"] == "FOREIGN KEY":
                fk_name = const["constraint_name"]
                col = const["column_name"]
                ref_table = const["foreign_table_name"]
                ref_col = const["foreign_column_name"]
                
                alter_query = f"ALTER TABLE `{table_name}` ADD CONSTRAINT `{fk_name}` FOREIGN KEY (`{col}`) REFERENCES `{ref_table}` (`{ref_col}`)"
                try:
                    my_cur.execute(alter_query)
                except Exception as e:
                    print(f"Warning: Could not add FK {fk_name}: {e}")

    # 3. Add Indices
    print("Adding indices...")
    for table_name in table_order:
        if table_name not in schema: continue
        table_info = schema[table_name]
        for idx in table_info["indices"]:
            if "UNIQUE" in idx["indexdef"] and "PRIMARY KEY" not in idx["indexdef"]:
                # Extract column from indexdef: ... (col1, col2)
                cols_part = idx["indexdef"].split("(")[-1].split(")")[0]
                my_cur.execute(f"CREATE UNIQUE INDEX `{idx['indexname']}` ON `{table_name}` ({cols_part})")
            elif "PRIMARY KEY" not in idx["indexdef"]:
                cols_part = idx["indexdef"].split("(")[-1].split(")")[0]
                my_cur.execute(f"CREATE INDEX `{idx['indexname']}` ON `{table_name}` ({cols_part})")

    # 4. Migrate Data
    print("Migrating data...")
    for table_name in table_order:
        print(f"Migrating {table_name}...")
        pg_cur.execute(f"SELECT * FROM {table_name}")
        rows = pg_cur.fetchall()
        
        if not rows:
            print(f"No data for {table_name}")
            continue
            
        columns = rows[0].keys()
        placeholders = ", ".join(["%s"] * len(columns))
        insert_query = f"INSERT INTO `{table_name}` ({', '.join(['`'+c+'`' for c in columns])}) VALUES ({placeholders})"
        
        data_to_insert = []
        for row in rows:
            val_list = []
            for col in columns:
                val = row[col]
                # Convert types for MySQL
                if isinstance(val, (datetime, date, time)):
                    val = str(val)
                elif isinstance(val, (dict, list)):
                    val = json.dumps(val)
                val_list.append(val)
            data_to_insert.append(tuple(val_list))
            
        my_cur.executemany(insert_query, data_to_insert)
        print(f"Migrated {len(rows)} rows to {table_name}")

    my_conn.commit()
    my_cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    pg_cur.close()
    pg_conn.close()
    my_cur.close()
    my_conn.close()
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
