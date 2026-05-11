import pandas as pd
import mysql.connector
import os
import sys
from datetime import datetime

# Add parent directory to path to import db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import DB_CONFIG

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def import_excel(file_path):
    print(f"Iniciando importação de {file_path}...")
    
    # Mapeamento de Atendentes
    attendant_map = {
        'VITOR': 'vitor.brito',
        'RAYSSA': 'rayssa.sousa',
        'WILLIAMS': 'williams.sobrinho',
        'LARA': 'lara.agra',
        'LAURA': 'laura.varela',
        'DAISY': 'daisy.barros',
        'ELAINE': 'elaine.ssilva',
        'RENAN': 'renan.caetano'
    }
    
    # Buscar IDs dos atendentes no banco
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, usuario FROM usuarios")
    db_users = {u['usuario'].lower(): u['id'] for u in cur.fetchall()}
    
    try:
        df = pd.read_excel(file_path)
        
        count = 0
        for index, row in df.iterrows():
            try:
                # 1. Limpeza de Dados
                nome = str(row['Nome Completo']).upper().strip()
                
                cpf = str(row['CPF']).strip()
                if cpf.upper().startswith('X'):
                    cpf = '0' + cpf[1:]
                
                # Apenas números para o CPF final (removendo pontos e traços se houver)
                cpf = ''.join(filter(str.isdigit, cpf))
                
                data_agendamento = row['Data/Hora']
                if isinstance(data_agendamento, str):
                    data_agendamento = datetime.strptime(data_agendamento, '%d/%m/%Y').date()
                elif hasattr(data_agendamento, 'date'):
                    data_agendamento = data_agendamento.date()
                
                # Mapeamento de Atendente
                atendente_raw = str(row['Atendente']).upper().strip()
                atendente_user = attendant_map.get(atendente_raw, atendente_raw.lower())
                atendente_id = db_users.get(atendente_user)
                
                # Campos fixos e mapeados
                payload = {
                    'nome_completo': nome,
                    'cpf': cpf,
                    'matricula': str(row.get('Matrícula', '')),
                    'cargo': str(row.get('Cargo', '')),
                    'vinculo': str(row.get('Tipo de Vínculo', '')),
                    'local_trabalho': str(row.get('Local de Trabalho', '')),
                    'email': str(row.get('E-mail', '')),
                    'tipo_servico': 'Atendimento Geral',
                    'observacao_problema': str(row.get('Serviço Principal', '')),
                    'observacao_solucao': 'Aguardando ser editado',
                    'tipo_atendimento': str(row.get('Atendimento', 'Presencial')).capitalize(),
                    'prioridade': 'Normal',
                    'status': 'concluido',
                    'is_import': 1,
                    'data_agendamento': data_agendamento,
                    'atendente_id': atendente_id,
                    'hora_inicio': '08:00', # Default past time
                    'hora_atendimento': datetime.combine(data_agendamento, datetime.min.time()),
                    'hora_conclusao': datetime.combine(data_agendamento, datetime.min.time())
                }
                
                # Inserção no Banco
                fields = list(payload.keys())
                placeholders = [f"%s"] * len(fields)
                query = f"INSERT INTO agendamentos ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
                
                cur.execute(query, list(payload.values()))
                count += 1
                
                if count % 50 == 0:
                    conn.commit()
                    print(f"Processados {count} registros...")
                    
            except Exception as e:
                print(f"Erro na linha {index + 2}: {e}")
                
        conn.commit()
        print(f"Importação concluída! Total de {count} registros inseridos.")
        
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 import_excel.py <caminho_do_arquivo>")
    else:
        import_excel(sys.argv[1])
