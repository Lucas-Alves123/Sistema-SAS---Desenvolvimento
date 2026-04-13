from flask import Blueprint, request, jsonify
from ..db import query_db
from datetime import datetime

solicitacoes_bp = Blueprint('solicitacoes', __name__)

def add_history(solicitacao_id, usuario_id, tipo_acao, anterior, novo):
    query = """
        INSERT INTO solicitacoes_historico (solicitacao_id, usuario_id, tipo_acao, valor_anterior, valor_novo)
        VALUES (%s, %s, %s, %s, %s)
    """
    query_db(query, (solicitacao_id, usuario_id, tipo_acao, str(anterior), str(novo)))

@solicitacoes_bp.route('/', methods=['GET'])
def list_solicitacoes():
    user_id = request.args.get('user_id')
    user_tipo = request.args.get('user_tipo')
    
    try:
        if user_tipo in ['adm', 'dev']:
            query = """
                SELECT s.*, u.nome_completo as solicitante_nome 
                FROM solicitacoes s 
                JOIN usuarios u ON s.solicitante_id = u.id 
                ORDER BY s.data_criacao DESC
            """
            params = ()
        else:
            if user_tipo == 'usuario':
                 query = """
                    SELECT s.*, u.nome_completo as solicitante_nome 
                    FROM solicitacoes s 
                    JOIN usuarios u ON s.solicitante_id = u.id 
                    ORDER BY s.data_criacao DESC
                """
                 params = ()
            else:
                query = """
                    SELECT s.*, u.nome_completo as solicitante_nome 
                    FROM solicitacoes s 
                    JOIN usuarios u ON s.solicitante_id = u.id 
                    WHERE s.solicitante_id = %s 
                    ORDER BY s.data_criacao DESC
                """
                params = (user_id,)
            
        results = query_db(query, params)
        for r in results:
            r['data_criacao'] = str(r['data_criacao'])
            # Map database 'Em análise' to display 'Análise'
            if r['status'] == 'Em análise':
                r['status'] = 'Análise'
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@solicitacoes_bp.route('/', methods=['POST'])
def create_solicitacao():
    data = request.json
    try:
        # Default status is 'Análise'
        query = """
            INSERT INTO solicitacoes (titulo, descricao, categoria, prioridade, solicitante_id, status) 
            VALUES (%s, %s, %s, %s, %s, 'Análise')
        """
        result = query_db(query, (data['titulo'], data['descricao'], data['categoria'], data['prioridade'], data['solicitante_id']))
        add_history(result['id'], data['solicitante_id'], 'Criação', None, 'Solicitação criada')
        return jsonify({'id': result['id'], 'message': 'Solicitação enviada com sucesso!'})
    except Exception as e:
        # Fallback if 'Análise' is not yet in ENUM (should have been added or mapped)
        try:
             query = """
                INSERT INTO solicitacoes (titulo, descricao, categoria, prioridade, solicitante_id, status) 
                VALUES (%s, %s, %s, %s, %s, 'Em análise')
            """
             result = query_db(query, (data['titulo'], data['descricao'], data['categoria'], data['prioridade'], data['solicitante_id']))
             add_history(result['id'], data['solicitante_id'], 'Criação', None, 'Solicitação criada')
             return jsonify({'id': result['id'], 'message': 'Solicitação enviada com sucesso!'})
        except:
             return jsonify({'error': str(e)}), 500

@solicitacoes_bp.route('/<int:id>', methods=['GET'])
def get_solicitacao(id):
    try:
        s = query_db("""
            SELECT s.*, u.nome_completo as solicitante_nome 
            FROM solicitacoes s 
            JOIN usuarios u ON s.solicitante_id = u.id 
            WHERE s.id = %s
        """, (id,), one=True)
        
        if not s: return jsonify({'error': 'Não encontrada'}), 404
        
        s['data_criacao'] = str(s['data_criacao'])
        if s['status'] == 'Em análise':
            s['status'] = 'Análise'
        
        comentarios = query_db("""
            SELECT c.*, u.nome_completo as usuario_nome, u.tipo as usuario_tipo 
            FROM solicitacoes_comentarios c 
            JOIN usuarios u ON c.usuario_id = u.id 
            WHERE c.solicitacao_id = %s 
            ORDER BY c.data_criacao ASC
        """, (id,))
        for c in comentarios:
            c['data_criacao'] = str(c['data_criacao'])
            
        return jsonify({'solicitacao': s, 'comentarios': comentarios})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@solicitacoes_bp.route('/<int:id>/status', methods=['PUT'])
def update_status(id):
    data = request.json
    usuario_id = data.get('usuario_id')
    user_tipo = data.get('user_tipo')
    novo_status = data.get('status')
    motivo_rejeicao = data.get('motivo_rejeicao')
    
    if user_tipo != 'dev':
        return jsonify({'error': 'Apenas desenvolvedores podem alterar o status das solicitações.'}), 403

    if user_tipo == 'usuario' and novo_status == 'Concluído':
        return jsonify({'error': 'Apenas administradores podem concluir solicitações.'}), 403

    try:
        current = query_db("SELECT status FROM solicitacoes WHERE id = %s", (id,), one=True)
        if not current: return jsonify({'error': 'Não encontrada'}), 404
        
        status_anterior = current['status']
        if status_anterior == 'Em análise': status_anterior = 'Análise'
        
        # Internal mapping
        backend_status = novo_status
        if novo_status == 'Análise': backend_status = 'Em análise'
        
        query = "UPDATE solicitacoes SET status = %s WHERE id = %s"
        params = [backend_status, id]
        
        if novo_status == 'Rejeitado' and motivo_rejeicao:
            query = "UPDATE solicitacoes SET status = %s, motivo_rejeicao = %s WHERE id = %s"
            params = [backend_status, motivo_rejeicao, id]
            
        query_db(query, tuple(params))
        add_history(id, usuario_id, 'Status', status_anterior, novo_status)
        return jsonify({'message': 'Status atualizado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@solicitacoes_bp.route('/<int:id>/comentarios', methods=['POST'])
def add_comentario(id):
    data = request.json
    try:
        query = "INSERT INTO solicitacoes_comentarios (solicitacao_id, usuario_id, mensagem) VALUES (%s, %s, %s)"
        query_db(query, (id, data['usuario_id'], data['mensagem']))
        return jsonify({'message': 'Mensagem enviada com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@solicitacoes_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    last_id = request.args.get('last_id', 0, type=int)
    try:
        # Check both names for compatibility during transition
        query = "SELECT COUNT(*) as count FROM solicitacoes WHERE status IN ('Análise', 'Em análise')"
        params = []
        if last_id > 0:
            query += " AND id > %s"
            params.append(last_id)
            
        count = query_db(query, tuple(params), one=True)
        return jsonify(count)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
