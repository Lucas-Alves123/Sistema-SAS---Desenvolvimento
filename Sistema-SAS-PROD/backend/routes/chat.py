from flask import Blueprint, request, jsonify
from ..db import query_db
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

# 1. Iniciar Sessão de Chat (Usado pelo solicitar.html)
@chat_bp.route('/sessao', methods=['POST'])
def criar_sessao():
    try:
        data = request.json
        nome = data.get('nome')
        cpf = data.get('cpf')
        assunto = data.get('assunto')
        
        if not nome:
            return jsonify({"error": "Nome é obrigatório"}), 400
            
        sql = """
            INSERT INTO chat_sessoes (participante_nome, participante_cpf, assunto, status)
            VALUES (%s, %s, %s, 'aguardando')
        """
        result = query_db(sql, (nome, cpf, assunto))
        sessao_id = result['id']

        # Mensagem automática de boas-vindas do sistema
        msg_sql = """
            INSERT INTO chat_mensagens (sessao_id, remetente_tipo, mensagem)
            VALUES (%s, 'sistema', 'Olá! Bem-vindo ao atendimento SAS. Para agilizarmos seu atendimento, por favor, me diga seu CPF e o que você precisa hoje.')
        """
        query_db(msg_sql, (sessao_id,))
        
        return jsonify({"success": True, "sessao_id": sessao_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. Listar Sessões (Para a Sidebar do Atendente)
@chat_bp.route('/sessoes', methods=['GET'])
def listar_sessoes():
    try:
        # Busca sessões aguardando ou em atendimento
        sql = """
            SELECT s.*, 
            (SELECT mensagem FROM chat_mensagens WHERE sessao_id = s.id ORDER BY id DESC LIMIT 1) as ultima_msg,
            (SELECT created_at FROM chat_mensagens WHERE sessao_id = s.id ORDER BY id DESC LIMIT 1) as ultima_msg_time
            FROM chat_sessoes s
            WHERE status != 'finalizado'
            ORDER BY s.ultimo_acesso DESC
        """
        sessoes = query_db(sql)
        
        # Serialização de datas
        for s in sessoes:
            s['created_at'] = str(s['created_at'])
            s['ultimo_acesso'] = str(s['ultimo_acesso'])
            if s.get('ultima_msg_time'): 
                s['ultima_msg_time'] = str(s['ultima_msg_time'])
                
        return jsonify(sessoes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. Enviar Mensagem
@chat_bp.route('/mensagem', methods=['POST'])
def enviar_mensagem():
    try:
        data = request.json
        sessao_id = data.get('sessao_id')
        remetente_tipo = data.get('remetente_tipo') # 'servidor' ou 'atendente'
        atendente_id = data.get('atendente_id')
        mensagem = data.get('mensagem')
        midia_url = data.get('midia_url')
        
        if not sessao_id or not mensagem:
            return jsonify({"error": "Dados incompletos"}), 400
            
        sql = """
            INSERT INTO chat_mensagens (sessao_id, remetente_tipo, atendente_id, mensagem, midia_url)
            VALUES (%s, %s, %s, %s, %s)
        """
        query_db(sql, (sessao_id, remetente_tipo, atendente_id, mensagem, midia_url))
        
        # Marcar sessão com notificação se for mensagem do servidor
        if remetente_tipo == 'servidor':
            query_db("UPDATE chat_sessoes SET notificacao_pendente = TRUE WHERE id = %s", (sessao_id,))
        else:
            query_db("UPDATE chat_sessoes SET notificacao_pendente = FALSE WHERE id = %s", (sessao_id,))
            
        return jsonify({"success": True}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 4. Obter Histórico de Mensagens
@chat_bp.route('/mensagens/<int:sessao_id>', methods=['GET'])
def buscar_mensagens(sessao_id):
    try:
        sql = """
            SELECT m.*, u.nome_completo as atendente_nome
            FROM chat_mensagens m
            LEFT JOIN usuarios u ON m.atendente_id = u.id
            WHERE m.sessao_id = %s
            ORDER BY m.id ASC
        """
        mensagens = query_db(sql, (sessao_id,))
        
        for m in mensagens:
            m['created_at'] = str(m['created_at'])
            
        # Ao carregar as mensagens, limpamos a notificação pendente
        query_db("UPDATE chat_sessoes SET notificacao_pendente = FALSE WHERE id = %s", (sessao_id,))
        
        return jsonify(mensagens)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 5. Atribuir Atendente ao Chat
@chat_bp.route('/atribuir/<int:sessao_id>', methods=['PUT'])
def atribuir_atendente(sessao_id):
    try:
        atendente_id = request.json.get('atendente_id')
        sql = "UPDATE chat_sessoes SET atendente_id = %s, status = 'em_atendimento' WHERE id = %s"
        query_db(sql, (atendente_id, sessao_id))
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 6. Finalizar Chat
@chat_bp.route('/finalizar/<int:sessao_id>', methods=['PUT'])
def finalizar_chat(sessao_id):
    try:
        query_db("UPDATE chat_sessoes SET status = 'finalizado' WHERE id = %s", (sessao_id,))
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 7. Colocar em Standby (Em Espera)
@chat_bp.route('/standby/<int:sessao_id>', methods=['PUT'])
def standby_chat(sessao_id):
    try:
        query_db("UPDATE chat_sessoes SET status = 'standby' WHERE id = %s", (sessao_id,))
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
