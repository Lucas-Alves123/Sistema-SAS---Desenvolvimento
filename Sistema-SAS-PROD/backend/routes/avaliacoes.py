from flask import Blueprint, request, jsonify
from backend.db import query_db
from datetime import datetime

avaliacoes_bp = Blueprint('avaliacoes', __name__)

@avaliacoes_bp.route('/', methods=['POST'])
def create_avaliacao():
    data = request.json
    required_fields = ['agendamento_id', 'tempo_espera', 'atendimento', 'estrutura_fisica', 'limpeza', 'resolucao_problema', 'clareza_informacoes']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo obrigatório ausente: {field}'}), 400

    try:
        # Check if already exists
        existing = query_db("SELECT id FROM avaliacoes WHERE agendamento_id = %s", (data['agendamento_id'],), one=True)
        if existing:
            return jsonify({'error': 'Este atendimento já foi avaliado.'}), 409

        query = """
            INSERT INTO avaliacoes 
            (agendamento_id, tempo_espera, atendimento, estrutura_fisica, limpeza, resolucao_problema, clareza_informacoes, comentarios)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['agendamento_id'], data['tempo_espera'], data['atendimento'], 
            data['estrutura_fisica'], data['limpeza'], data['resolucao_problema'], 
            data['clareza_informacoes'], data.get('comentarios', '')
        )
        
        result = query_db(query, params)
        if result and isinstance(result, dict) and 'id' in result:
            return jsonify({'message': 'Avaliação enviada com sucesso!', 'id': result['id']}), 201
        return jsonify({'message': 'Avaliação enviada com sucesso!'}), 201

    except Exception as e:
        print(f"Error creating avaliacao: {e}")
        return jsonify({'error': 'Erro interno ao salvar avaliação.'}), 500

@avaliacoes_bp.route('/', methods=['GET'])
def list_avaliacoes():
    try:
        query = """
            SELECT av.*, a.nome_completo, a.cpf, u.nome_completo as atendente_nome, a.tipo_servico
            FROM avaliacoes av
            JOIN agendamentos a ON av.agendamento_id = a.id
            LEFT JOIN usuarios u ON a.atendente_id = u.id
            ORDER BY av.created_at DESC
        """
        results = query_db(query)
        
        if results:
            for r in results:
                if r.get('created_at'):
                    r['created_at'] = str(r['created_at'])
                    
        return jsonify(results or [])
        
    except Exception as e:
        print(f"Error listing avaliacoes: {e}")
        return jsonify({'error': str(e)}), 500
