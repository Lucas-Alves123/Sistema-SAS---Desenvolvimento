import mysql.connector
from datetime import date

# Credenciais
DB_HOST = "10.24.56.110"
DB_NAME = "sas_sga"
DB_USER = "sas_sga"
DB_PASS = "tCRkCckF79qAH9LO"
DB_PORT = 3306

def force_promote():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
        )
        cur = conn.cursor(dictionary=True)
        hoje = date.today().isoformat()

        # 1. Verificar se o painel está livre
        cur.execute("""
            SELECT id FROM agendamentos 
            WHERE status = 'pendente' 
            AND data_agendamento = %s 
            AND (tipo_atendimento = 'Presencial' OR tipo_atendimento IS NULL)
        """, (hoje,))
        busy = cur.fetchone()

        if busy:
            print(f"[INFO] Painel ainda ocupado pelo ID {busy['id']}. Vou resetá-lo primeiro.")
            cur.execute("UPDATE agendamentos SET status = 'chegou' WHERE id = %s", (busy['id'],))
            conn.commit()

        # 2. Promover o próximo da fila
        cur.execute("""
            SELECT id, nome_completo FROM agendamentos 
            WHERE status = 'na_fila_do_painel' 
            AND data_agendamento = %s 
            ORDER BY id ASC LIMIT 1
        """, (hoje,))
        next_item = cur.fetchone()

        if next_item:
            print(f"[SUCCESS] Promovendo ID {next_item['id']} ({next_item['nome_completo']}) para o painel!")
            cur.execute("UPDATE agendamentos SET status = 'pendente' WHERE id = %s", (next_item['id'],))
            conn.commit()
        else:
            print("[INFO] Ninguém na fila do painel para promover.")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Erro na promoção forçada: {e}")

if __name__ == "__main__":
    force_promote()
