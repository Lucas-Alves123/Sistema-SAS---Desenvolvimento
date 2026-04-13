from flask import Blueprint, request, jsonify
from backend.db import query_db

identificacao_bp = Blueprint('identificacao', __name__)

@identificacao_bp.route('/validar', methods=['GET'])
def validar_servidor():
    valor = request.args.get('valor', '').strip()
    # Simple print for monitoring (will show up in service logs)
    print(f"[SEARCH] Received request for: {valor}")
    
    if not valor:
        return jsonify({'success': False, 'message': 'Informe um CPF ou matrícula válido.'}), 400

    # Remove non-numeric characters for CPF search
    valor_limpo = ''.join(filter(str.isdigit, valor))
    
    server_data = None
    
    # 1. Tentar buscar por CPF (se tiver 11 dígitos ou for numérico)
    if valor_limpo and len(valor_limpo) == 11:
        query_cpf = """
            SELECT 
                t.nome_completo, 
                t.cpf, 
                t.email, 
                v.numero_funcional as matricula, 
                v.especialidade as cargo, 
                v.tipo_vinculo as vinculo, 
                v.unidade_lotacao as local_trabalho
            FROM trabalhadores t
            LEFT JOIN vinculos_trabalhadores v ON t.id = v.trabalhador_id
            WHERE t.cpf = %s OR t.cpf = %s
        """
        try:
            server_data = query_db(query_cpf, (valor_limpo, valor))
        except Exception as e:
            print(f"CPF Query Error: {e}")

    # 2. Se não achou por CPF, tenta por Matrícula (numero_funcional)
    if not server_data:
        query_matricula = """
            SELECT 
                t.nome_completo, 
                t.cpf, 
                t.email, 
                v.numero_funcional as matricula, 
                v.especialidade as cargo, 
                v.tipo_vinculo as vinculo, 
                v.unidade_lotacao as local_trabalho
            FROM vinculos_trabalhadores v
            JOIN trabalhadores t ON v.trabalhador_id = t.id
            WHERE v.numero_funcional = %s
        """
        try:
            server_data = query_db(query_matricula, (valor,))
        except Exception as e:
            print(f"Matricula Query Error: {e}")

    if server_data:
        return jsonify({
            'success': True,
            'data': server_data
        })
    else:
        return jsonify({'success': False, 'message': 'Servidor não encontrado'}), 404
