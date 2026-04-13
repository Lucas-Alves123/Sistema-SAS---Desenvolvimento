import mysql.connector
from datetime import date

# Credenciais
DB_HOST = "10.24.56.110"
DB_NAME = "sas_sga"
DB_USER = "sas_sga"
DB_PASS = "tCRkCckF79qAH9LO"
DB_PORT = 3306

def nuke():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
        )
        cur = conn.cursor(dictionary=True)
        hoje = date.today().isoformat()

        # Resetando TUDO que for Presencial e Pendente hoje
        cur.execute("""
            UPDATE agendamentos 
            SET status = 'chegou' 
            WHERE status = 'pendente' 
            AND data_agendamento = %s
            AND (tipo_atendimento = 'Presencial' OR tipo_atendimento IS NULL)
        """, (hoje,))
        
        affected = cur.rowcount
        conn.commit()
        
        print(f"[SUCCESS] Foram resetados {affected} agendamentos. O painel deve estar livre agora!")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Falha no nuke: {e}")

if __name__ == "__main__":
    nuke()
