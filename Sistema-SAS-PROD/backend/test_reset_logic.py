import sys
import os
from datetime import datetime

# Ajusta o path para importar o DB
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from db import query_db
    print("[INFO] DB importado com sucesso.")
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"[INFO] Processando para a data: {today}")

    # 1. Tentar rodar a lógica de reset
    res = query_db("""
        UPDATE agendamentos 
        SET status = 'chegou' 
        WHERE status = 'pendente' 
        AND data_agendamento = %s
        AND (tipo_atendimento = 'Presencial' OR tipo_atendimento IS NULL)
    """, (today,))
    
    print(f"[SUCCESS] Lógica de Reset executada. Registros afetados: {res}")

    # 2. Tentar rodar a lógica de promoção (manual)
    waiting = query_db("""
        SELECT id, nome_completo FROM agendamentos 
        WHERE status = 'na_fila_do_painel' 
        AND data_agendamento = %s 
        ORDER BY id ASC LIMIT 1
    """, (today,), one=True)
    
    if waiting:
        print(f"[INFO] Encontrado na fila: {waiting['id']} ({waiting['nome_completo']})")
        query_db("UPDATE agendamentos SET status = 'pendente' WHERE id = %s", (waiting['id'],))
        print(f"[SUCCESS] Promovido para o painel com sucesso!")
    else:
        print("[INFO] Ninguém na fila para promover.")

except Exception as e:
    print(f"[ERROR] Falha crítica no teste: {e}")
    import traceback
    traceback.print_exc()
