import sys
import os
import csv
import logging
import mysql.connector

# Adiciona o diretório Sistema-SAS-PROD ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import Config

# Configura log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FILE_FUNCIONARIOS = os.path.join(os.path.dirname(__file__), '..', 'relatorio.csv', 'LISTA_LISTA_FUNCIONARIOS_185482_.csv')
FILE_SETORES = os.path.join(os.path.dirname(__file__), '..', 'relatorio.csv', 'SETORES_SGP - 2026.06.15.csv')

VINCULO_MAP = {
    'EST': 'Estatutário',
    'COM': 'Comissionado',
    'CTD': 'CTD (Contrato)',
    'EXQ': 'Extraquadro',
    'EXM': 'Extraquadro',
    'EXTRA QUADRO INTERNO': 'Extraquadro',
    'EXTRA QUADRO EXTERNO': 'Extraquadro',
    'SERVIDOR EFETIVO': 'Estatutário'
}

def get_conn():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASS,
        port=Config.DB_PORT,
        ssl_disabled=True
    )

def load_setores():
    setores = {}
    try:
        with open(FILE_SETORES, mode='r', encoding='latin-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                setor_code = str(row.get('setor', '')).strip()
                nome_setor = str(row.get('nomesetor', '')).strip()
                if setor_code:
                    setores[setor_code] = nome_setor
        logging.info(f"{len(setores)} setores carregados do CSV.")
    except Exception as e:
        logging.error(f"Erro ao ler setores: {e}")
    return setores

def pad_cpf(cpf):
    cpf = str(cpf).strip()
    if not cpf:
        return ''
    return cpf.zfill(11)

def format_telefone(tel, cel):
    tel = str(tel).strip()
    cel = str(cel).strip()
    
    if tel == '0': tel = ''
    if cel == '0': cel = ''
    
    if tel and not cel:
        return tel
    elif not tel and cel:
        return cel
    elif tel and cel:
        if tel == cel:
            return tel
        else:
            return f"{tel} // {cel}"
    return ''

def format_matricula(numfunc, numvinc):
    numfunc = str(numfunc).strip()
    numvinc = str(numvinc).strip()
    try:
        vinc_int = int(numvinc)
        numvinc_formatted = f"{vinc_int:02d}"
    except ValueError:
        numvinc_formatted = numvinc.zfill(2)
    return f"{numfunc}/{numvinc_formatted}"

def main():
    setores = load_setores()
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    
    logging.info("Limpando a tabela vinculos_trabalhadores...")
    cur.execute("TRUNCATE TABLE vinculos_trabalhadores;")
    conn.commit()
    
    funcionarios_processados = 0
    vinculos_inseridos = 0
    
    with open(FILE_FUNCIONARIOS, mode='r', encoding='latin-1') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        insert_worker_query = """
            INSERT INTO trabalhadores (nome_completo, cpf, telefone, email) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            nome_completo = VALUES(nome_completo), 
            telefone = VALUES(telefone), 
            email = VALUES(email)
        """
        
        insert_vinc_query = """
            INSERT INTO vinculos_trabalhadores 
            (trabalhador_id, numero_funcional, tipo_vinculo, especialidade, unidade_lotacao, situacao)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        for row in reader:
            situacao_vinculo = str(row.get('SITUACAO_VINCULO', '')).strip()
            if not situacao_vinculo:
                continue
                
            tipo_vinc_raw = str(row.get('TIPOVINC', '')).strip().upper()
            if tipo_vinc_raw == 'CLT':
                continue
            
            tipo_vinculo_sistema = VINCULO_MAP.get(tipo_vinc_raw, tipo_vinc_raw)
            cpf = pad_cpf(row.get('CPF', ''))
            if not cpf:
                continue
                
            nome = str(row.get('NOME', '')).strip()
            email = str(row.get('E_MAIL', '')).strip()
            tel_raw = row.get('TELEFONE', '')
            cel_raw = row.get('NUMTEL_CELULAR', '')
            telefone_final = format_telefone(tel_raw, cel_raw)
            
            numfunc = row.get('NUMFUNC', '')
            numvinc = row.get('NUMVINC', '')
            matricula = format_matricula(numfunc, numvinc)
            nome_cargo = str(row.get('NOME_CARGO', '')).strip()
            lotacao_code = str(row.get('LOTACAO', '')).strip()
            unidade_lotacao = setores.get(lotacao_code, lotacao_code)
            
            trabalhador_id = None
            try:
                cur.execute(insert_worker_query, (nome, cpf, telefone_final, email))
                conn.commit()
                cur.execute("SELECT id FROM trabalhadores WHERE cpf = %s", (cpf,))
                worker_record = cur.fetchone()
                if worker_record:
                    trabalhador_id = worker_record['id']
            except Exception as e:
                logging.error(f"Erro ao inserir trabalhador {cpf}: {e}")
                conn.rollback()
                continue
            
            if trabalhador_id:
                funcionarios_processados += 1
                try:
                    cur.execute(insert_vinc_query, (trabalhador_id, matricula, tipo_vinculo_sistema, nome_cargo, unidade_lotacao, situacao_vinculo))
                    conn.commit()
                    vinculos_inseridos += 1
                except Exception as e:
                    logging.error(f"Erro ao inserir vínculo para trabalhador {cpf}: {e}")
                    conn.rollback()

    cur.close()
    conn.close()
    logging.info(f"Importação concluída. Trabalhadores processados: {funcionarios_processados}. Vínculos inseridos: {vinculos_inseridos}.")

if __name__ == '__main__':
    main()
