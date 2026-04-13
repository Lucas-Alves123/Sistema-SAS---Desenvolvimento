import mysql.connector
from datetime import date

# Credenciais do config.py
DB_HOST = "10.24.56.110"
DB_NAME = "sas_sga"
DB_USER = "sas_sga"
DB_PASS = "tCRkCckF79qAH9LO"
DB_PORT = 3306

def list_all_today():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
        )
        cur = conn.cursor(dictionary=True)
        hoje = date.today().isoformat()

        print(f"--- STATUS DOS AGENDAMENTOS DE HOJE ({hoje}) ---")
        cur.execute("SELECT id, nome_completo, status, tipo_atendimento, atendente_id FROM agendamentos WHERE data_agendamento = %s", (hoje,))
        res = cur.fetchall()
        
        if not res:
            print("Nenhum agendamento encontrado para hoje.")
        else:
            for r in res:
                print(f"ID: {r['id']} | Status: {r['status']} | Nome: {r['nome_completo']} | Tipo: {r['tipo_atendimento']} | Atendente: {r['atendente_id']}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    list_all_today()
