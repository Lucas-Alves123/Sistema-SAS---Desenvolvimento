from flask import Blueprint, request, jsonify
from backend.db import query_db

identificacao_bp = Blueprint('identificacao', __name__)

@identificacao_bp.route('/validar', methods=['GET'])
def validar_servidor():
    valor = request.args.get('valor', '').strip()
    
    if not valor:
        return jsonify({'success': False, 'message': 'Informe um CPF ou matrícula válido.'}), 400

    # Remove non-numeric characters for CPF search
    valor_limpo = ''.join(filter(str.isdigit, valor))
    
    nome_servidor = None
    
    # 1. Tentar buscar por CPF (se tiver 11 dígitos ou for numérico)
    # Busca direta na tabela trabalhadores
    if valor_limpo and len(valor_limpo) == 11:
        query_cpf = """
            SELECT nome_completo
            FROM trabalhadores
            WHERE cpf = %s OR cpf = %s
            LIMIT 1
        """
        result = query_db(query_cpf, (valor_limpo, valor), one=True)
        if result:
            nome_servidor = result['nome_completo']

    # 2. Se não achou por CPF, tenta por Matrícula (numero_funcional)
    # Busca na tabela vinculos_trabalhadores e relaciona com trabalhadores
    if not nome_servidor:
        query_matricula = """
            SELECT t.nome_completo
            FROM vinculos_trabalhadores v
            JOIN trabalhadores t ON v.trabalhador_id = t.id
            WHERE v.numero_funcional = %s
            LIMIT 1
        """
        result = query_db(query_matricula, (valor,), one=True)
        if result:
            nome_servidor = result['nome_completo']

    if nome_servidor:
        return jsonify({
            'success': True,
            'nome_completo': nome_servidor
        })
    else:
        return jsonify({'success': False, 'message': 'Servidor não encontrado'}), 404
