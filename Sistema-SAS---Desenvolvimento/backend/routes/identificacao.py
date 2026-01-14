from flask import Blueprint, request, jsonify
from backend.db import query_db

identificacao_bp = Blueprint('identificacao', __name__)

@identificacao_bp.route('/validar', methods=['GET'])
def validar_servidor():
    import logging
    
    # Configure file logging
    logging.basicConfig(filename='debug_search.log', level=logging.INFO, 
                        format='%(asctime)s - %(message)s')
    
    valor = request.args.get('valor', '').strip()
    logging.info(f"REQUEST RECEIVED: valor='{valor}'")
    print(f"DEBUG: Received search request for: {valor}")
    
    if not valor:
        logging.warning("Empty value received")
        return jsonify({'success': False, 'message': 'Informe um CPF ou matrícula válido.'}), 400

    # Remove non-numeric characters for CPF search
    valor_limpo = ''.join(filter(str.isdigit, valor))
    logging.info(f"Cleaned value for CPF check: '{valor_limpo}'")
    
    server_data = None
    
    # 1. Tentar buscar por CPF (se tiver 11 dígitos ou for numérico)
    if valor_limpo and len(valor_limpo) == 11:
        logging.info("Attempting CPF search...")
        query_cpf = """
            SELECT 
                t.nome_completo, 
                t.cpf, 
                NULL as email, 
                v.numero_funcional as matricula, 
                NULL as cargo, 
                NULL as vinculo, 
                NULL as local_trabalho
            FROM trabalhadores t
            LEFT JOIN vinculos_trabalhadores v ON t.id = v.trabalhador_id
            WHERE t.cpf = %s OR t.cpf = %s
            LIMIT 1
        """
        try:
            server_data = query_db(query_cpf, (valor_limpo, valor), one=True)
            logging.info(f"CPF Search Result: {server_data}")
        except Exception as e:
            logging.error(f"CPF Query Error: {e}")

    # 2. Se não achou por CPF, tenta por Matrícula (numero_funcional)
    if not server_data:
        logging.info("Attempting Matricula search...")
        query_matricula = """
            SELECT 
                t.nome_completo, 
                t.cpf, 
                NULL as email, 
                v.numero_funcional as matricula, 
                NULL as cargo, 
                NULL as vinculo, 
                NULL as local_trabalho
            FROM vinculos_trabalhadores v
            JOIN trabalhadores t ON v.trabalhador_id = t.id
            WHERE v.numero_funcional = %s
            LIMIT 1
        """
        try:
            server_data = query_db(query_matricula, (valor,), one=True)
            logging.info(f"Matricula Search Result: {server_data}")
        except Exception as e:
            logging.error(f"Matricula Query Error: {e}")

    if server_data:
        logging.info("Server FOUND")
        return jsonify({
            'success': True,
            'data': server_data
        })
    else:
        logging.warning("Server NOT FOUND")
        return jsonify({'success': False, 'message': 'Servidor não encontrado'}), 404
