import mysql.connector
from datetime import date

# Credenciais extraídas do config.py
DB_HOST = "10.24.56.110"
DB_NAME = "sas_sga"
DB_USER = "sas_sga"
DB_PASS = "tCRkCckF79qAH9LO"
DB_PORT = 3306

def fix_panel():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        cur = conn.cursor(dictionary=True)
        hoje = date.today().isoformat()

        # 1. Identificar chamados travados (Pendente hoje - sem filtro rigoroso de data para garantir limpeza)
        cur.execute("""
            SELECT id, nome_completo FROM agendamentos 
            WHERE status = 'pendente'
        """)
        stuck = cur.fetchall()

        if not stuck:
            print("[INFO] Nenhum agendamento travado com status 'pendente' encontrado.")
            return

        print(f"[INFO] Encontrados {len(stuck)} agendamentos travando o painel.")
        
        for item in stuck:
            print(f"  - Resetando ID {item['id']} ({item['nome_completo']}) para 'chegou'")
            cur.execute("UPDATE agendamentos SET status = 'chegou' WHERE id = %s", (item['id'],))

        conn.commit()
        print("[SUCCESS] Painel destravado com sucesso!")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Falha ao destravar painel: {e}")

if __name__ == "__main__":
    fix_panel()
