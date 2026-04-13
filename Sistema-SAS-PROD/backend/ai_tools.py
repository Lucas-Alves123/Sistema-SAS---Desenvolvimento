from backend.db import query_db
from datetime import datetime

def obter_resumo_fila_hoje() -> dict:
    """
    Retorna o resumo da fila de espera de hoje do sistema SAS em tempo real.
    Sempre chame esta função quando o usuário perguntar coisas como: "como está a fila", "quantas pessoas tem aguardando", "qual o movimento de hoje", "como está o SAS hoje".
    Retorna as contagens de quem está aguardando, em atendimento e já foi finalizado.
    """
    hoje = datetime.now().strftime('%Y-%m-%d')
    try:
        aguardando = query_db("SELECT COUNT(*) as qtd FROM agendamentos WHERE data_agendamento = %s AND status IN ('chegou', 'na_fila_do_painel')", (hoje,), one=True)
        atendendo = query_db("SELECT COUNT(*) as qtd FROM agendamentos WHERE data_agendamento = %s AND status IN ('em_andamento', 'pendente')", (hoje,), one=True)
        finalizados = query_db("SELECT COUNT(*) as qtd FROM agendamentos WHERE data_agendamento = %s AND status = 'concluido'", (hoje,), one=True)
        
        return {
            "aguardando_na_recepcao": aguardando['qtd'] if aguardando else 0,
            "em_atendimento_nas_mesas": atendendo['qtd'] if atendendo else 0,
            "atendimentos_completados_hoje": finalizados['qtd'] if finalizados else 0,
            "data_da_pesquisa": hoje
        }
    except Exception as e:
        return {"erro_ao_consultar_banco": str(e)}

def obter_status_atendentes() -> dict:
    """
    Retorna o status atual dos atendentes físicos do SAS.
    Sempre chame esta função quando o usuário perguntar: "quem está online", "quais atendentes estão logados", "tem alguém em pausa", "quantos atendentes temos".
    Retorna o nome e o status atual de cada atendente logado no sistema.
    """
    try:
        # Busca no banco e calcula a diferença do ultimo acesso
        usuarios = query_db("""
            SELECT nome_completo, status_atendimento, motivo_pausa, 
            TIMESTAMPDIFF(SECOND, ultimo_acesso, NOW()) as segundos_inativo 
            FROM usuarios 
            WHERE tipo = 'usuario' AND situacao = 'ativo'
        """)
        
        atendentes_ativos = []
        if usuarios:
            for u in usuarios:
                is_online = (u['segundos_inativo'] is not None and u['segundos_inativo'] < 120)
                status = u['status_atendimento']
                
                # Se não contatou a API nos ultimos 120s, ele caiu / fechou navegador
                if not is_online:
                    status = 'offline'
                
                # Só nos importamos com quem está no prédio logado (mesmo se em pausa)
                if status != 'offline':
                    atendentes_ativos.append({
                        "nome": u['nome_completo'].split()[0], # Somente o primeiro nome para a IA falar mais natural
                        "status_atual": status,
                        "motivo_pausa_se_houver": u['motivo_pausa'] if status == 'pausa' else None
                    })
                    
        return {
            "quantidade_total_conectados": len(atendentes_ativos),
            "detalhes_de_cada_atendente": atendentes_ativos
        }
    except Exception as e:
        return {"erro_ao_consultar_banco": str(e)}

def alterar_meu_status_banco(user_id: int, novo_status: str, motivo_pausa: str = "") -> dict:
    """
    ESSA É UMA FERRAMENTA DE AÇÃO (Pode alterar o banco de dados e agir diretamente no sistema vivo).
    Use esta ferramenta quando o usuário disser que "vai almoçar", "precisa sair", "vai entrar em pausa", ou "voltou".
    Por favor, você deve extrair o 'user_id' correspondente do CONTEXTO de Identidade que passamos via prompt para ter acesso seguro.
    
    Argumentos:
    - user_id: (Obrigatório) ID numérico do usuário logado (presente no prompt que você recebeu).
    - novo_status: Escolha estritamente entre 'online', 'pausa', ou 'offline'.
    - motivo_pausa: Requerido APENAS SE novo_status for 'pausa' (ex: 'Almoço', 'Banheiro'). Deixe em branco caso contrário.
    """
    try:
        if str(novo_status).lower() not in ['online', 'pausa', 'offline']:
            return {"erro": "Status invalido. Escolha 'online', 'pausa' ou 'offline'."}
        
        status_db = 'presencial' if str(novo_status).lower() == 'online' else str(novo_status).lower()
        motivo = motivo_pausa if status_db == 'pausa' else None
        
        query_db("UPDATE usuarios SET status_atendimento = %s, motivo_pausa = %s WHERE id = %s", 
                 (status_db, motivo, user_id))
        return {
            "sucesso": True, 
            "mensagem_acao_executada": f"UPDATE executado na tabela usuarios. Novo status: {status_db}.",
            "user_id_afetado": user_id
        }
    except Exception as e:
        return {"erro_fatal_ao_modificar_banco": str(e)}

# Lista exportada para o Gemini no ai.py
SAS_AGENTS = [obter_resumo_fila_hoje, obter_status_atendentes, alterar_meu_status_banco]
