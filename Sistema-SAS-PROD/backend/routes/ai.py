from flask import Blueprint, request, jsonify
import json
import os
import random
import google.generativeai as genai
import difflib
import unicodedata
import re
from datetime import datetime
from backend.config import Config
from google.generativeai.types import content_types

# Importando o novo "Cérebro Jarvis" - Funções do sistema SAS
from backend.ai_tools import SAS_AGENTS, obter_resumo_fila_hoje, obter_status_atendentes, alterar_meu_status_banco

ai_bp = Blueprint('ai', __name__)

def remove_accents(input_str):
    if not input_str:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

# Base path for knowledge file
KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), '..', 'ai_knowledge.json')

# Configure Gemini
api_key = getattr(Config, 'GEMINI_API_KEY', None)
if api_key:
    genai.configure(api_key=api_key)
    # Using gemini-2.0-flash as it is available and stable
    model_name = 'models/gemini-2.0-flash'
    model = genai.GenerativeModel(model_name, tools=SAS_AGENTS)
else:
    model = None

def load_knowledge():
    try:
        if os.path.exists(KNOWLEDGE_PATH):
            with open(KNOWLEDGE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading AI knowledge: {e}")
    return {"servicos": [], "faq": [], "slang": {}, "typos": {}, "modulos": [], "tutoriais": [], "social": {}, "institucional": {}}

def normalize_message(message, knowledge):
    # 1. Handle slangs and common abbreviations
    words = message.split()
    slang_map = knowledge.get('slang', {})
    normalized_words = [slang_map.get(w, w) for w in words]
    
    # 2. Dynamic Typo Correction for System Keywords
    system_keywords = set()
    for mod in knowledge.get('modulos', []):
        system_keywords.add(mod['nome'].lower())
        if 'id' in mod: system_keywords.add(mod['id'].lower())
    for ser in knowledge.get('servicos', []):
        system_keywords.add(ser['nome'].lower())
    for tut in knowledge.get('tutoriais', []):
        system_keywords.add(tut['topico'].lower())
        for kw in tut.get('keywords', []):
            system_keywords.add(kw.lower())
    for term in knowledge.get('glossario', {}).keys():
        system_keywords.add(term.lower())

    final_words = []
    typo_map = knowledge.get('typos', {})
    
    # Pre-calculate no-accent keywords for better matching
    keywords_list = list(system_keywords)
    keywords_no_accents = [remove_accents(kw) for kw in keywords_list]
    
    for word in normalized_words:
        word_lower = word.lower()
        word_no_accents = remove_accents(word_lower)
        
        if word_lower in typo_map:
            final_words.append(typo_map[word_lower])
            continue
            
        # Try direct match with no accents
        if word_no_accents in keywords_no_accents:
            idx = keywords_no_accents.index(word_no_accents)
            final_words.append(keywords_list[idx])
            continue

        matches = difflib.get_close_matches(word_no_accents, keywords_no_accents, n=1, cutoff=0.7)
        if matches:
            idx = keywords_no_accents.index(matches[0])
            final_words.append(keywords_list[idx])
        else:
            final_words.append(word)
    
    message = " ".join(final_words)

    if 'comprimento' in message and any(x in message for x in ['ola', 'oi', 'bom dia', 'boa tarde', 'boa noite', 'ajuda', 'tudo bem', 'suporte']):
        message = message.replace('comprimento', 'cumprimento')
                
    return message

def local_logic_handler(message):
    msg = remove_accents(message.lower().strip())
    
    # Simple Math (e.g., 1+1, 2 * 5, quanto é 10/2)
    math_match = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', msg)
    if math_match:
        try:
            val1 = int(math_match.group(1))
            op = math_match.group(2)
            val2 = int(math_match.group(3))
            if op == '+': res = val1 + val2
            elif op == '-': res = val1 - val2
            elif op == '*': res = val1 * val2
            elif op == '/': res = val1 / val2 if val2 != 0 else "infinito"
            return f"Essa é fácil! {val1} {op} {val2} é igual a **{res}**. 🧠"
        except: pass

    # Identity / Role / Creator
    if any(x in msg for x in ["quem e voce", "quem e tu", "seu nome"]):
        return "Eu sou o **SAS Assistente**, sua inteligência artificial e manual digital do sistema. Estou aqui para facilitar sua vida no SAS! 🚀"
    
    if any(x in msg for x in ["quem o criou", "quem te criou", "quem te fez", "quem e o dono", "quem desenvolveu", "quem e o desenvolvedor"]):
        return "Fui desenvolvido com excelência por **Lucas Mateus Alves Luna** para modernizar o atendimento ao servidor! 👨‍💻✨"

    # Logic to identify if user is asking about the SAS overall, even with grammar errors or missing words
    sas_terms = {"sas", "setor", "central", "servico"}
    intent_terms = {"que", "oque", "oq", "pra", "serve", "finalidade", "objetivo", "horario", "horas", "sobre", "explicar", "funciona"}
    exact_phrases = ["o que e o sas", "o que e esse sistema", "sistema sas", "para que serve", "qual sua finalidade", "qual o objetivo", "pra que serve", "atendimento ao servidor", "sobre o sas", "horario de"]
    
    msg_words = set(msg.split())
    is_asking_about_sas = any(phrase in msg for phrase in exact_phrases)
    if not is_asking_about_sas:
        if (msg_words.intersection(sas_terms) and msg_words.intersection(intent_terms)) or ("sas" in msg_words and len(msg_words) <= 3) or ("setor" in msg_words and len(msg_words) <= 3):
            is_asking_about_sas = True
            
    if is_asking_about_sas:
        return "O **SAS (Serviço de Atendimento ao Servidor)** foi criado para concentrar, em um único ambiente, a prestação de serviços da área administrativa da Secretaria de Saúde de Pernambuco.\n\n💡 **Nosso Objetivo:** Aprimorar o relacionamento entre a Secretaria de Saúde de Pernambuco e seus servidores, garantindo acesso às informações com qualidade, eficiência e transparência, promovendo um atendimento ágil e resolutivo.\n\n⏰ **Horário de Atendimento:** 8h às 17h."

    if any(x in msg for x in ["o que voce faz", "como funciona", "me ajude", "socorro", "o que faz", "assistente faz", "manual", "como usar"]):
        return "Eu sou um especialista no Sistema SAS! Minha função é ser seu **Manual Digital**. Posso te explicar o que cada botão faz (como no Atendimento ou Agendamento), te dizer quais documentos levar para um serviço ou até tirar dúvidas sobre o seu uso. O que quer aprender agora? 📖✨"

    # Date / Time
    if any(x in msg for x in ["que horas", "que dia", "data de hoje", "horario"]):
        now = datetime.now()
        return f"Hoje é dia **{now.strftime('%d/%m/%Y')}** e agora são **{now.strftime('%H:%M')}**. Em que mais posso te ajudar?"

    return None

def get_gemini_reply(prompt, knowledge, history=None, user_context=None):
    if not model:
        return None

    # Build identity block if user data was provided by the frontend
    identity_block = ""
    if user_context:
        try:
            u = json.loads(user_context) if isinstance(user_context, str) else user_context
            user_id = u.get('id', '?')
            user_name = u.get('nome', 'Usuário')
            user_tipo = u.get('tipo', '').upper()
            identity_block = f"""
    IDENTIDADE DO OPERADOR (Contexto de Segurança):
    - A pessoa que está falando com você agora é: **{user_name}** (ID do sistema: {user_id}, Nível: {user_tipo}).
    - Chame-o pelo primeiro nome de forma natural e amigável.
    - TRAVA DE SEGURANÇA: Quando usar a ferramenta `alterar_meu_status_banco`, você DEVE sempre usar o user_id = {user_id}. Nunca altere o status de outro usuário.
"""
        except Exception:
            pass

    context = f"""
    CAPA:
    - Você é o Gemini, integrado ao sistema SAS.
    - Você tem acesso aos dados do SAS (abaixo), mas também possui TODO o seu conhecimento geral de IA.
    - Responda QUALQUER pergunta do usuário. 
    - Se for sobre o sistema SAS, use o manual abaixo.
    - Se for uma pergunta jurídica, administrativa ou geral, use sua inteligência geral para responder.
    
    REGRAS DE FORMATAÇÃO OBRIGATÓRIAS:
    1. Responda SEMPRE em formato de Tópicos ou Passo-a-Passo.
    2. Use listas com marcadores (-) ou números (1., 2.).
    3. Destaque palavras-chave e nomes de botões em **negrito**.
    4. Seja prestativo, claro e use emojis com moderação para deixar a leitura ágil e agradável.
    5. Nunca retorne um bloco de texto gigante. Separe em parágrafos curtos.
    
    BASE DE CONHECIMENTO SAS:
    1. MÓDULOS: {json.dumps(knowledge.get('modulos'), ensure_ascii=False)}
    2. SERVIÇOS/DOCUMENTOS: {json.dumps(knowledge.get('servicos'), ensure_ascii=False)}
    3. TUTORIAIS: {json.dumps(knowledge.get('tutoriais'), ensure_ascii=False)}
    """
    
    messages = []
    if history:
        # Keep only last 5 for context to keep it fast and relevant
        for msg in history[-5:]:
            role = "user" if msg['role'] == 'user' else "model"
            messages.append({"role": role, "parts": [msg['content']]})
    
    try:
        chat = model.start_chat(history=messages)
        # Combine context and prompt to ensure Gemini follows rules strictly
        full_prompt = f"{context}{identity_block}\n\nUsuário: {prompt}"
        response = chat.send_message(full_prompt)
        
        # J.A.R.V.I.S. Loop: Check and execute AI Tools
        max_tool_calls = 3 # Prevent infinite loops
        calls = 0
        while calls < max_tool_calls:
            if response.candidates and response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]
                if part.function_call:
                    fc = part.function_call
                    function_name = fc.name
                    
                    if function_name == "obter_resumo_fila_hoje":
                        res = obter_resumo_fila_hoje()
                    elif function_name == "obter_status_atendentes":
                        res = obter_status_atendentes()
                    elif function_name == "alterar_meu_status_banco":
                        args = dict(fc.args)
                        res = alterar_meu_status_banco(
                            user_id=int(args.get('user_id', 0)),
                            novo_status=str(args.get('novo_status', '')),
                            motivo_pausa=str(args.get('motivo_pausa', ''))
                        )
                    else:
                        res = {"error": "Função desconhecida"}
                    
                    # Return the Python dict directly via from_function_response
                    function_response_part = content_types.Part.from_function_response(
                        name=function_name,
                        response={"result": res}
                    )
                    # Send execution result back to Gemini so it can generate final text
                    response = chat.send_message(function_response_part)
                    calls += 1
                else:
                    break
            else:
                break

        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            return "Puxa, meu 'cérebro' (IA) está um pouco cansado agora devido ao limite de uso gratuito. 😅 Mas não se preocupe! Eu ainda conheço tudo sobre o SAS pelo meu manual local. Pode me perguntar sobre módulos ou serviços que eu te respondo na hora!"
        
        with open(os.path.join(os.path.dirname(__file__), '..', 'ai_error.log'), 'a') as f:
            f.write(f"Gemini API Error ({model_name}): {error_msg}\n")
        return None

def fuzzy_find(raw_message, normalized_message, knowledge, history=None, user_context=None):
    message_clean = normalized_message.lower().strip()
    message_no_accents = remove_accents(message_clean)
    
    # 0. Check Local Logic/Math/Identity first
    local_res = local_logic_handler(normalized_message)
    if local_res: return local_res

    social = knowledge.get('social', {})
    greetings = social.get('greetings', [])
    small_talk = social.get('small_talk', {})

    # 1. First priority: Check social greetings and small talk
    # Using string search instead of split to catch "primeiramente, bom dia"
    for g in greetings:
        if g in message_clean:
            return random.choice(social.get('responses', ["Olá! Como posso ajudar?"]))

    for key, response in small_talk.items():
        if key in message_clean:
            return response
    
    # 2. Check Glossary (to avoid API quota issues for common terms)
    glossary = knowledge.get('glossario', {})
    message_no_accents = remove_accents(message_clean)
    
    for term, definition in glossary.items():
        term_clean = term.lower().strip()
        if term_clean in message_clean or remove_accents(term_clean) in message_no_accents:
            return definition

    # 3. Check Real Cases (Experience FAQ) - Training from veteran attendants
    for caso in knowledge.get('casos_reais', []):
        # Match by ID or variations
        if caso['id'].lower() in message_clean:
            return caso['solucao']
        for var in caso.get('variacoes', []):
            var_clean = var.lower().strip()
            if var_clean in message_clean or remove_accents(var_clean) in message_no_accents:
                return caso['solucao']

    clarification_keywords = ["detalhe", "detalhar", "mais sobre", "explique", "explicar", "entendi nada", "ficou confuso", "pode explicar"]
    is_clarification = any(ck in message_clean for ck in clarification_keywords)

    # 3. Robust Tutorial/Module Matching (Fallback for API failures or complex phrases)
    # Check if ANY core keywords are in the normalized message
    for tut in knowledge.get('tutoriais', []):
        topic_lower = tut['topico'].lower()
        keywords = [kw.lower() for kw in tut.get('keywords', [])]
        if topic_lower in message_clean or any(kw in message_clean for kw in keywords):
            # If it's a clarification, still try Gemini first, but we have this fallback
            if is_clarification:
                clarification_prompt = f"O usuário pediu mais detalhes sobre {tut['topico']}. Use estes passos: {tut['passos']} e explique de forma humana."
                res = get_gemini_reply(clarification_prompt, knowledge, history)
                if res: return res
            
            # Local fallback response (Humanized steps)
            steps_str = "\n".join([f"- {s}" for s in tut['passos']])
            return f"Claro! Sobre **{tut['topico'].capitalize()}**, aqui está o que você precisa saber:\n\n{steps_str}\n\nPosso te ajudar com mais algum detalhe desse processo?"

    # 4. Global Search for Modules/Services in Knowledge Base
    for mod in knowledge.get('modulos', []):
        if mod['nome'].lower() in message_clean or mod['id'].lower() in message_clean:
            return f"O módulo **{mod['nome']}** serve para: {mod['descricao']}. \nRecursos principais: {', '.join(mod.get('recursos', mod.get('campos', [])))}"

    for ser in knowledge.get('servicos', []):
        if ser['nome'].lower() in message_clean:
            docs = "\n".join([f"- {d}" for d in ser['documentos']])
            return f"Para o serviço de **{ser['nome']}**, você vai precisar de:\n\n{docs}\n\nAjudo em algo mais?"

    # 5. Last Resort: Gemini Brain (for anything else)
    gemini_reply = get_gemini_reply(raw_message, knowledge, history, user_context=user_context)
    if gemini_reply:
        return gemini_reply

    return "Hm, não consegui processar essa agora. Sou o Assistente do SAS e estou em constante aprendizado. Pode tentar perguntar de outra forma?"

@ai_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    raw_message = data.get('message', '').strip()
    history = data.get('history', [])
    user_context = data.get('user_context', None)  # [FASE 3] Identidade do operador
    
    if not raw_message:
        return jsonify({'reply': "Oi! Como posso te ajudar hoje?", 'type': 'text'})
    
    knowledge = load_knowledge()
    normalized_message = normalize_message(raw_message.lower(), knowledge)
    reply = fuzzy_find(raw_message, normalized_message, knowledge, history, user_context=user_context)
    
    return jsonify({'reply': reply, 'type': 'text'})

@ai_bp.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    message_id = data.get('message_id')
    is_positive = data.get('is_positive')
    feedback_text = data.get('feedback', '')
    original_message = data.get('original_message', '')
    ai_response = data.get('ai_response', '')

    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message_id": message_id,
        "is_positive": is_positive,
        "feedback": feedback_text,
        "original_message": original_message,
        "ai_response": ai_response
    }

    try:
        log_path = os.path.join(os.path.dirname(__file__), '..', 'ai_feedback.log')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Failed to log feedback: {e}")

    return jsonify({"status": "success", "message": "Feedback recorded"}), 200
