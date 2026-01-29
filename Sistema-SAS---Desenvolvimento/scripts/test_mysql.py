import mysql.connector

MYSQL_CONFIG = {
    "host": "10.24.56.110",
    "database": "sas_sga",
    "user": "sas_sga",
    "password": "tCRkCckF79qAH9LO",
    "port": 3306
}

def test_connection():
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        print("Successfully connected to MySQL server!")
        conn.close()
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")

if __name__ == "__main__":
    test_connection()
