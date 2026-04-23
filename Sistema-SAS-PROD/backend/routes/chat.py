from flask import Blueprint, request, jsonify
from ..db import query_db
from datetime import datetime
import requests
import json

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

# ----------------------------------------------------------------------------
# LOGICA DE WHATSAPP / WEBHOOK (BOT)
# ----------------------------------------------------------------------------

def send_whatsapp_message(number, text):
    """
    Função auxiliar para enviar mensagens via API de WhatsApp (Ex: Evolution, Z-API)
    """
    # CONFIGURAÇÃO DA SUA API (Preencha aqui quando tiver os dados)
    API_URL = "SUA_URL_DA_API_AQUI"
    API_KEY = "SUA_KEY_AQUI"
    INSTANCE = "SUA_INSTANCIA_AQUI"

    if "SUA_URL" in API_URL:
        print(f"[WA Simulation] Enviar para {number}: {text}")
        return True

    payload = {
        "number": number,
        "message": text
    }
    headers = {
        "Content-Type": "application/json",
        "apikey": API_KEY
    }
    
    try:
        url = f"{API_URL}/message/sendText/{INSTANCE}"
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        return res.status_code in [200, 201]
    except Exception as e:
        print(f"[WA Error] Falha ao enviar: {e}")
        return False

@chat_bp.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """
    Webhook para receber mensagens do WhatsApp e responder automaticamente (BOT)
    """
    try:
        data = request.json
        # Ajuste esses campos dependendo de qual API de WhatsApp você usar
        # Exemplo para Evolution API:
        sender_number = ""
        message_text = ""
        
        if data.get('data') and data['data'].get('key'):
             sender_number = data['data']['key'].get('remoteJid', '').split('@')[0]
             message_text = data['data'].get('message', {}).get('conversation', '')
        else:
             # Fallback genérico
             sender_number = data.get('from', '').split('@')[0]
             message_text = data.get('text', '')

        print(f"[WEBHOOK] Mensagem de {sender_number}: {message_text}")

        # --- TRAVA DE SEGURANÇA (BETA TESTER) ---
        # Apenas o seu número receberá a resposta automática por enquanto
        ALLOWED_NUMBER = "5581982985213"
        if ALLOWED_NUMBER not in sender_number:
            print(f"[WEBHOOK] Ignorando número {sender_number} (Fora da Whitelist)")
            return jsonify({"status": "ignored"}), 200

        # --- LÓGICA DO BOT ---
        welcome_text = (
            "Bom dia! 👋\n\n"
            "Este canal é destinado ao Atendimento ao Servidor da Secretaria Estadual de Saúde (SES-PE).\n\n"
            "📞 *Aviso:* Não realizamos ligações e não é possível ouvir áudios por aqui.\n\n"
            "Para registrar seu atendimento e entrar na fila, clique no link abaixo e preencha seus dados:\n\n"
            "🔗 https://sas.pe.gov.br/solicitar\n\n"
            "Agradecemos a compreensão."
        )

        success = send_whatsapp_message(sender_number, welcome_text)
        
        return jsonify({"success": success, "number": sender_number}), 200

    except Exception as e:
        print(f"[WEBHOOK Error]: {e}")
        return jsonify({"error": str(e)}), 500
