import csv
import mysql.connector
import os
import sys
from datetime import datetime

# DB Config directly here to avoid import errors
DB_CONFIG = {
    'host': "10.24.56.110",
    'database': "sas_sga",
    'user': "sas_sga",
    'password': "tCRkCckF79qAH9LO",
    'port': 3306
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def import_csv(file_path):
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
        # Abrindo com latin-1 para lidar com acentos da planilha
        with open(file_path, mode='r', encoding='latin-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            count = 0
            for row in reader:
                try:
                    # 1. Limpeza de Dados
                    nome = str(row.get('Nome Completo', '')).upper().strip()
                    if not nome: continue

                    cpf_raw = str(row.get('CPF', '')).strip()
                    if cpf_raw.upper().startswith('X'):
                        cpf = '0' + cpf_raw[1:]
                    else:
                        cpf = cpf_raw
                    
                    # Apenas números para o CPF final
                    cpf = ''.join(filter(str.isdigit, cpf))
                    
                    data_raw = row.get('Data/Hora', '')
                    try:
                        # Tenta converter data no formato DD/MM/YYYY
                        data_agendamento = datetime.strptime(data_raw.split(' ')[0], '%d/%m/%Y').date()
                    except:
                        continue
                    
                    # Mapeamento de Atendente
                    atendente_raw = str(row.get('Atendente', '')).upper().strip()
                    atendente_user = attendant_map.get(atendente_raw, atendente_raw.lower())
                    atendente_id = db_users.get(atendente_user)
                    
                    # Campos mapeados
                    payload = {
                        'nome_completo': nome,
                        'cpf': cpf,
                        'matricula': str(row.get('Matrícula', '') or row.get('Matrcula', '')),
                        'cargo': str(row.get('Cargo', '')),
                        'vinculo': str(row.get('Tipo de Vínculo', '') or row.get('Tipo de Vnculo', '')),
                        'local_trabalho': str(row.get('Local de Trabalho', '')),
                        'email': str(row.get('E-mail', '')),
                        'tipo_servico': 'Atendimento Geral',
                        'observacao_problema': str(row.get('Serviço Principal', '') or row.get('Servio Principal', '')),
                        'observacao_solucao': 'Aguardando ser editado',
                        'tipo_atendimento': str(row.get('Atendimento', 'Presencial')).capitalize(),
                        'prioridade': 'Normal',
                        'status': 'concluido',
                        'is_import': 1,
                        'data_agendamento': data_agendamento,
                        'atendente_id': atendente_id,
                        'hora_inicio': '08:00',
                        'hora_atendimento': datetime.combine(data_agendamento, datetime.min.time()),
                        'hora_conclusao': datetime.combine(data_agendamento, datetime.min.time())
                    }
                    
                    # Inserção no Banco
                    fields = list(payload.keys())
                    placeholders = ["%s"] * len(fields)
                    query = f"INSERT INTO agendamentos ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
                    
                    cur.execute(query, list(payload.values()))
                    count += 1
                    
                    if count % 100 == 0:
                        conn.commit()
                        print(f"Processados {count} registros...")
                        
                except Exception as e:
                    print(f"Erro ao processar linha: {e}")
            
            conn.commit()
            print(f"Importação concluída! Total de {count} registros inseridos.")
            
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 import_csv.py <caminho_do_arquivo>")
    else:
        import_csv(sys.argv[1])
