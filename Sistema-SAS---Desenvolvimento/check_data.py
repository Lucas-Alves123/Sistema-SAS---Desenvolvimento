import psycopg2
from backend.config import Config

def check_data():
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            port=Config.DB_PORT
        )
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM trabalhadores")
        count_t = cur.fetchone()[0]
        print(f"Trabalhadores count: {count_t}")
        
        if count_t > 0:
            cur.execute("SELECT * FROM trabalhadores LIMIT 1")
            print("Sample trabalhador:", cur.fetchone())
            
        cur.execute("SELECT COUNT(*) FROM vinculos_trabalhadores")
        count_v = cur.fetchone()[0]
        print(f"Vinculos count: {count_v}")
        
        if count_v > 0:
            cur.execute("SELECT * FROM vinculos_trabalhadores LIMIT 1")
            print("Sample vinculo:", cur.fetchone())
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()
