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
    
    # 1. Tentar buscar por CPF (se tiver até 11 dígitos)
    if valor_limpo and len(valor_limpo) <= 11:
        cpf_buscado = valor_limpo.zfill(11)
        query_cpf = """
            SELECT 
                t.nome_completo, 
                t.cpf, 
                t.email, 
                t.telefone,
                v.numero_funcional as matricula, 
                v.especialidade as cargo, 
                v.tipo_vinculo as vinculo, 
                v.unidade_lotacao as local_trabalho,
                v.situacao
            FROM trabalhadores t
            LEFT JOIN vinculos_trabalhadores v ON t.id = v.trabalhador_id
            WHERE (t.cpf = %s OR t.cpf = %s)
        """
        try:
            raw_data = query_db(query_cpf, (cpf_buscado, valor))
            if raw_data:
                # Filtra apenas ativos
                server_data = [d for d in raw_data if str(d.get('situacao')).upper() == 'ATIVO' or not d.get('situacao')]
        except Exception as e:
            print(f"CPF Query Error: {e}")

    # 2. Se não achou por CPF (ou só achou inativos), tenta por Matrícula (numero_funcional)
    if not server_data:
        query_matricula = """
            SELECT 
                t.nome_completo, 
                t.cpf, 
                t.email, 
                t.telefone,
                v.numero_funcional as matricula, 
                v.especialidade as cargo, 
                v.tipo_vinculo as vinculo, 
                v.unidade_lotacao as local_trabalho,
                v.situacao
            FROM vinculos_trabalhadores v
            JOIN trabalhadores t ON v.trabalhador_id = t.id
            WHERE v.numero_funcional = %s
        """
        try:
            raw_data = query_db(query_matricula, (valor,))
            if raw_data:
                # Filtra apenas ativos
                server_data = [d for d in raw_data if str(d.get('situacao')).upper() == 'ATIVO' or not d.get('situacao')]
        except Exception as e:
            print(f"Matricula Query Error: {e}")

    is_history = False
    
    # 3. Se ainda não achou, tenta no histórico de agendamentos/atendimentos
    if not server_data and (valor_limpo and len(valor_limpo) <= 11):
        cpf_buscado = valor_limpo.zfill(11)
        query_historico = """
            SELECT 
                nome_completo, 
                cpf, 
                email, 
                matricula, 
                cargo, 
                vinculo, 
                local_trabalho,
                telefone
            FROM agendamentos
            WHERE cpf = %s OR cpf = %s
            ORDER BY id DESC
        """
        try:
            raw_historico = query_db(query_historico, (cpf_buscado, valor))
            if raw_historico:
                unique_vinculos = []
                seen = set()
                for h in raw_historico:
                    # Cria uma chave única baseada na matrícula e vínculo
                    v_key = f"{h.get('matricula') or ''}-{h.get('vinculo') or ''}".strip()
                    if v_key not in seen:
                        seen.add(v_key)
                        unique_vinculos.append(h)
                server_data = unique_vinculos
                is_history = True
        except Exception as e:
            print(f"Historico Query Error: {e}")

    if server_data:
        return jsonify({
            'success': True,
            'is_history': is_history,
            'data': server_data
        })
    else:
        return jsonify({'success': False, 'message': 'Servidor não encontrado'}), 404
