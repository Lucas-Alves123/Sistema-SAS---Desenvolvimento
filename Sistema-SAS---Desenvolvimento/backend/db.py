import mysql.connector
from mysql.connector import Error
from .config import Config

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            port=Config.DB_PORT
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        # Use dictionary=True to get results as dicts (similar to RealDictCursor)
        cur = conn.cursor(dictionary=True)
        
        # Convert %s to %s (MySQL also uses %s for placeholders in mysql-connector)
        cur.execute(query, args)
        
        if cur.with_rows:
            rv = cur.fetchall()
            conn.commit()
            cur.close()
            conn.close()
            return (rv[0] if rv else None) if one else rv
        else:
            conn.commit()
            last_id = cur.lastrowid
            cur.close()
            conn.close()
            # If it was an INSERT, return the last inserted ID in a dict to mimic RETURNING id
            if query.strip().upper().startswith("INSERT"):
                return {"id": last_id}
            return None
    except Error as e:
        print(f"Database query error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise e
