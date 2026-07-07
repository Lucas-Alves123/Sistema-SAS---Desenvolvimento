import sys
import os
import glob
import logging
import mysql.connector
import pandas as pd

# Adiciona o diretório Sistema-SAS-PROD ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import Config

# Configura log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

relatorio_dir = os.path.join(os.path.dirname(__file__), '..', 'relatorio.csv')
arquivos_funcionarios = glob.glob(os.path.join(relatorio_dir, 'LISTA_LISTA_FUNCIONARIOS_*.xlsx'))

if not arquivos_funcionarios:
    logging.error("Nenhum arquivo XLSX de funcionários encontrado na pasta relatorio.csv")
    sys.exit(1)

FILE_FUNCIONARIOS = max(arquivos_funcionarios, key=os.path.getmtime)
logging.info(f"Arquivo selecionado para importação: {FILE_FUNCIONARIOS}")
FILE_SETORES = os.path.join(os.path.dirname(__file__), '..', 'relatorio.csv', 'SETORES_SGP - 2026.06.15.xlsx')

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
        df = pd.read_excel(FILE_SETORES, dtype=str)
        df.fillna('', inplace=True)
        for _, row in df.iterrows():
            setor_code = str(row.get('setor', '')).strip()
            nome_setor = str(row.get('nomesetor', '')).strip()
            if setor_code.endswith('.0'):
                setor_code = setor_code[:-2]
            if setor_code and setor_code not in setores:
                setores[setor_code] = nome_setor
        logging.info(f"{len(setores)} setores carregados do Excel.")
    except Exception as e:
        logging.error(f"Erro ao ler setores: {e}")
    return setores

def pad_cpf(cpf):
    cpf = str(cpf).strip()
    if not cpf or cpf == 'nan':
        return ''
    if cpf.endswith('.0'):
        cpf = cpf[:-2]
    return cpf.zfill(11)

def format_telefone(tel, cel):
    tel = str(tel).strip()
    cel = str(cel).strip()
    if tel == 'nan': tel = ''
    if cel == 'nan': cel = ''
    if tel.endswith('.0'): tel = tel[:-2]
    if cel.endswith('.0'): cel = cel[:-2]
    
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
    if numfunc.endswith('.0'): numfunc = numfunc[:-2]
    if numvinc.endswith('.0'): numvinc = numvinc[:-2]
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
    
    try:
        df = pd.read_excel(FILE_FUNCIONARIOS, dtype=str)
        df.fillna('', inplace=True)
    except Exception as e:
        logging.error(f"Erro ao ler arquivo de funcionários: {e}")
        return

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
    
    for i, row in df.iterrows():
        situacao_vinculo = str(row.get('SITUACAO_VINCULO', '')).strip()
        if not situacao_vinculo or situacao_vinculo == 'nan':
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
        if email == 'nan': email = ''
        tel_raw = str(row.get('TELEFONE', ''))
        cel_raw = str(row.get('NUMTEL_CELULAR', ''))
        telefone_final = format_telefone(tel_raw, cel_raw)
        
        numfunc = str(row.get('NUMFUNC', ''))
        numvinc = str(row.get('NUMVINC', ''))
        matricula = format_matricula(numfunc, numvinc)
        nome_cargo = str(row.get('NOME_CARGO', '')).strip()
        if nome_cargo == 'nan': nome_cargo = ''
        
        lotacao_code = str(row.get('LOTACAO', '')).strip()
        if lotacao_code.endswith('.0'): lotacao_code = lotacao_code[:-2]
        unidade_lotacao = setores.get(lotacao_code, lotacao_code)
        
        trabalhador_id = None
        try:
            cur.execute(insert_worker_query, (nome, cpf, telefone_final, email))
            cur.execute("SELECT id FROM trabalhadores WHERE cpf = %s", (cpf,))
            worker_record = cur.fetchone()
            if worker_record:
                trabalhador_id = worker_record['id']
        except Exception as e:
            logging.error(f"Erro ao inserir trabalhador {cpf}: {e}")
            continue
        
        if trabalhador_id:
            funcionarios_processados += 1
            try:
                cur.execute(insert_vinc_query, (trabalhador_id, matricula, tipo_vinculo_sistema, nome_cargo, unidade_lotacao, situacao_vinculo))
                vinculos_inseridos += 1
            except Exception as e:
                logging.error(f"Erro ao inserir vínculo para trabalhador {cpf}: {e}")
        
        if i % 2000 == 0:
            conn.commit()

    # Commit final dos registros restantes
    conn.commit()

    cur.close()
    conn.close()
    logging.info(f"Importação concluída. Trabalhadores processados: {funcionarios_processados}. Vínculos inseridos: {vinculos_inseridos}.")

if __name__ == '__main__':
    main()
