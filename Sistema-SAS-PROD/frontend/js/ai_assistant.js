(function () {
    window.SAS = window.SAS || {};
    window.SAS.ai = {};

    const CHAT_TITLE = "SAS Assistente";
    const WELCOME_MSG = "Olá! Eu sou o seu **Manual Digital do SAS**. Posso te ajudar com o passo a passo de como usar o sistema. O que você quer aprender agora?";
    const QUICK_QUESTIONS = [
        "Como transferir atendimento?",
        "Esqueci minha senha, e agora?",
        "Qual o horário de funcionamento?",
        "Para que serve o SAS?",
        "Diferença entre Cancelar e Pausar"
    ];

    const LOCAL_KNOWLEDGE = [
        {
            keywords: [["ctc"], ["tempo", "contribuicao"], ["certidao", "contribuicao"]],
            question: "Para solicitar a CTC (Certidão de Tempo de Contribuição), precisamos saber o seu status atual. Você é servidor ativo ou já se desligou?",
            options: [
                "Sou Servidor Ativo",
                "Sou Ex-Servidor (Desligado/Inativo)"
            ]
        },
        {
            keywords: [["ctc", "ativo"], ["ctc", "servidor", "ativo"], ["tempo", "contribuicao", "ativo"], ["sou servidor ativo"]],
            answer: "Como você **continua na ativa**, não é possível solicitar a CTC. Para levar seu tempo para o INSS, você deve solicitar apenas a **Declaração de Vínculo**."
        },
        {
            keywords: [["ctc", "desligado"], ["ctc", "ex-servidor"], ["ctc", "inativo"], ["tempo", "contribuicao", "desligado"], ["ex-servidor", "desligado"]],
            answer: "Para solicitar a **CTC** (Certidão de Tempo de Contribuição), o requerimento correto é o **Requerimento A**."
        },
        {
            keywords: [["cts"]],
            answer: "Para solicitar a **CTS**, você deve preencher e enviar o **Requerimento de CTS**."
        },
        {
            keywords: [["nome", "errado"], ["nome", "retificar"], ["nome", "mae"], ["regularizacao", "funcional"], ["retificacao"], ["retificar"]],
            answer: "Para retificar dados incorretos no cadastro (como o nome da mãe, por exemplo), o servidor deve dar entrada na **Regularização Funcional**."
        },
        {
            keywords: [["exoneracao"], ["acumulo", "vinculo"], ["notificacao", "estado"]],
            answer: "Para dar entrada em **exoneração** (ex: notificação de acúmulo de vínculos), deve ser fornecido o **Requerimento A**."
        },
        {
            keywords: [["salario", "desconto"], ["motivo", "desconto"], ["desconto"]],
            answer: "Para analisar o motivo de o salário vir com desconto, é preciso preencher o **Requerimento A**."
        },
        {
            keywords: [["dtc"]],
            question: "Existem algumas situações diferentes sobre a DTC. Sobre o que você deseja saber?",
            options: [
                "DTC para Aposentadoria",
                "DTC para Averbação",
                "DTC (Regra Geral)"
            ]
        },
        {
            keywords: [["dtc", "aposentadoria"]],
            answer: "Para solicitar a **DTC para fins de Aposentadoria**, é preciso preencher o **Requerimento A**."
        },
        {
            keywords: [["dtc", "averbacao"]],
            answer: "Para solicitar a **DTC para Averbação**, é preciso preencher o **Requerimento A**."
        },
        {
            keywords: [["dtc", "geral"], ["dtc", "regra", "geral"], ["dtc", "rgps"]],
            answer: "Para solicitar a **DTC**, regra geral (incluindo ao RGPS), é preciso preencher o **Requerimento A**."
        },
        {
            keywords: [["processo", "nao", "tem", "numero"], ["saber", "processo", "numero"], ["andamento", "processo", "sem", "numero"], ["numero", "processo"]],
            answer: "Caso deseje saber de um processo mas não tenha o número, você deve solicitar o número na unidade onde deu entrada."
        },
        {
            keywords: [["mudar", "email"], ["mudar", "telefone"], ["alterar", "email"], ["alterar", "telefone"], ["atualizar", "telefone"], ["telefone"]],
            answer: "Para mudar seu e-mail ou número de telefone, você deve preencher o **Requerimento A** solicitando **Regularização Funcional**."
        },
        {
            keywords: [["problema", "pagamento"], ["problema", "frequencia"], ["folha", "ponto", "desconto"], ["pagamento"], ["contracheque"]],
            answer: "Para problemas de pagamento, frequência ou descontos integrais no salário por falha na folha de ponto, você deve dar entrada no **Requerimento A** e anexar os contracheques referidos."
        },
        {
            keywords: [["ppp"], ["ltcat"]],
            answer: "Para solicitação de **PPP**, é preciso preencher o formulário do **PPP**, **LTCAT** e o **Requerimento A**."
        },
        {
            keywords: [["direito", "ferias"], ["programar", "ferias"], ["ferias"]],
            answer: "Para verificar direito a férias ou programá-las, você deve procurar a **sua chefia imediata**."
        },
        {
            keywords: [["encerra", "contrato"], ["encerrar", "contrato"], ["finalizar", "contrato"]],
            answer: "Para saber como encerrar seu contrato de trabalho, é preciso entrar em contato com a **sua unidade**."
        },
        {
            keywords: [["receber", "pl"], ["recebeu", "pl"]],
            answer: "Caso tenha parado de receber a PL, é preciso preencher o **Requerimento A**."
        },
        {
            keywords: [["preencheu", "requerimento", "nao", "tem", "sei"], ["nao", "tem", "numero", "sei"], ["sem", "numero", "sei"]],
            answer: "Se você preencheu um requerimento e ainda não tem o número do SEI, deve enviar o requerimento para o **e-mail do Protocolo Geral**."
        },
        {
            keywords: [["folha", "ponto", "negaram"], ["folha", "ponto", "negada"], ["relacao", "frequencia"]],
            answer: "Se você precisa comprovar frequência e a unidade negar a folha de ponto, você deve solicitar a **relação de frequência** via **Requerimento A**."
        },
        {
            keywords: [["orientacoes", "aposentadoria"], ["entrada", "aposentadoria"], ["checklist", "aposentadoria"]],
            answer: "Para orientações sobre aposentadoria (esclarecimento de vínculos e licenças-prêmio), deve ser fornecido o **Checklist de Aposentadoria** juntamente com o telefone do Atendimento ao Servidor."
        },
        {
            keywords: [["entrada", "licenca", "premio"], ["concessao", "licenca", "premio"], ["decenio", "licenca"], ["dar entrada na licenca premio"]],
            answer: "Para dar entrada na licença prêmio (ex: 4º decênio), deve-se pedir a **concessão da licença prêmio** (para fins de aposentadoria ou gozo) com o Requerimento A, e aguardar publicação no Diário Oficial."
        },
        {
            keywords: [["aposentadoria", "ferias"], ["aposentadoria", "licenca"], ["gozar", "ferias", "aposentadoria"]],
            answer: "É fortemente orientado que você **goze todas as suas férias e licenças-prêmio** pendentes antes de dar entrada na aposentadoria."
        },
        {
            keywords: [["quanto", "tempo", "aposentadoria"], ["abono", "permanencia"], ["saber quanto tempo falta para aposentadoria"]],
            answer: "Para saber quanto tempo falta para poder dar entrada na aposentadoria, o servidor é orientado a solicitar o **Abono de Permanência**."
        },
        {
            keywords: [["aposentadoria"]],
            question: "Entendi que você tem dúvidas sobre aposentadoria. O que exatamente você deseja saber?",
            options: [
                "Orientações para dar entrada na aposentadoria",
                "Saber quanto tempo falta para aposentadoria"
            ]
        },
        {
            keywords: [["piso", "salarial"], ["receber", "piso"], ["valor", "piso"], ["piso"]],
            answer: "Para solicitações referentes a **piso salarial** (valores a receber ou retroativos de uma unidade específica), você deve verificar diretamente com a **sua unidade de origem**. (Obs: não há impedimento de dar entrada via Requerimento A, mas a análise dependerá da unidade)."
        },
        {
            keywords: [["reducao", "carga", "horaria"], ["neurodivergencia"], ["reducao"]],
            answer: "Para solicitar a **redução de carga horária** (ex: portadores de neurodivergencia ou necessidades especiais), deve ser preenchido o formulário específico de redução de carga horária para dar entrada na SAD."
        },
        {
            keywords: [["corrigir", "pasep"], ["pasep"], ["nao", "recebeu", "pasep"], ["nao", "recebe", "pis"], ["pis"]],
            answer: "Para solicitar correção, alteração ou informações sobre o não recebimento do seu **PIS/PASEP**, você deve preencher o **Requerimento A**."
        },
        {
            keywords: [["averbar", "tempo"], ["averbar", "ctc"], ["averbacao"], ["averbar"]],
            answer: "Para fazer a **averbação de tempo** (como por exemplo averbação de CTC), você deve preencher o **Requerimento A**."
        },
        {
            keywords: [["gozo", "licenca", "premio", "assinatura"], ["licenca", "premio", "sem", "assinatura"]],
            answer: "A solicitação de gozo de licença prêmio **só é válida mediante a assinatura da chefia imediata**. Não é possível dar entrada sem a autorização e assinatura da sua chefia."
        },
        {
            keywords: [["tempo", "inss"], ["levar", "inss"], ["contrato", "inss"]],
            answer: "Para levar o tempo do seu contrato para o INSS, você deve solicitar a **DTC**."
        },
        {
            keywords: [["marcar", "pericia"], ["tipo", "pericia"], ["duvida", "pericia", "medica"], ["pericia"]],
            answer: "Para dúvidas sobre marcação ou tipo de perícia médica, você pode ligar para o número **(81) 99488-3044** para falar diretamente com a perícia."
        },
        {
            keywords: [["atualizar", "conta", "banco"], ["mudar", "conta"], ["alterar", "dados", "bancarios"], ["troca", "conta", "bancaria"], ["trocar", "conta"], ["conta", "banco"], ["dados", "bancarios"]],
            answer: "Para solicitar a atualização ou troca da sua conta de banco:\n- **Servidores da ativa**: Devem preencher o **Requerimento A**.\n- **Aposentados/Pensionistas**: Devem procurar a **FUNAPE**."
        },
        {
            keywords: [["vem", "problema"], ["cartao", "vem"], ["vem"]],
            answer: "Para problemas com o cartão VEM, o ideal é procurar primeiro o atendimento do próprio VEM. Se necessário, você pode solicitar um novo **Termo de Adesão**."
        },
        {
            keywords: [["remocao", "perseguicao"], ["remocao", "local", "trabalho"], ["perseguicao"], ["remocao"]],
            answer: "Para solicitar remoção do seu local de trabalho, independentemente do motivo, você deve preencher o **Requerimento A**."
        },
        {
            keywords: [["comprovar", "carga", "horaria"], ["declaracao", "vinculo"], ["carga", "horaria"]],
            answer: "Para comprovar sua carga horária, você deve solicitar a **Declaração de Vínculo**."
        },
        {
            keywords: [["certidao", "nao", "averbei", "inss"], ["certidao", "inss"], ["declaracao", "nao", "averbei"], ["declaracao", "nao", "averbacao"]],
            answer: "Para solicitar uma certidão ou declaração informando que não averbou nenhum tempo no INSS, você deve preencher o **Requerimento A**."
        },
        {
            keywords: [["motivo", "licenca", "premio"], ["demora", "licenca", "premio"], ["atraso", "licenca", "premio"]],
            answer: "A data de publicação da Licença Prêmio pode sofrer alterações devido a **faltas ou outras ocorrências** (ex: no início da sua carreira). Para consultar o motivo exato, é necessário realizar uma consulta ao seu histórico no **SGP**."
        },
        {
            keywords: [["email", "protocolo"], ["reenviar", "email", "protocolo"], ["abertura", "processo", "sei"]],
            answer: "Após a abertura do processo no sistema SEI (ou envio do e-mail para o protocolo), orienta-se **entrar em contato novamente em 10 dias** para obter informações sobre o andamento. É necessário informar o número do processo SEI disponibilizado pelo setor de protocolo."
        },
        {
            keywords: [["funape"]],
            question: "Encontrei alguns serviços relacionados à FUNAPE. Qual o seu caso?",
            options: [
                "Trocar conta bancária"
            ]
        },
        {
            keywords: [["inss"]],
            question: "Temos algumas situações envolvendo o INSS. Qual é a sua necessidade?",
            options: [
                "Levar tempo de contrato para o INSS",
                "Certidão de não averbei no INSS"
            ]
        },
        {
            keywords: [["licenca", "premio"]],
            question: "Sobre qual aspecto da Licença Prêmio você quer saber?",
            options: [
                "Dar entrada na licença prêmio",
                "Motivo de demora/atraso da licença prêmio",
                "Licença prêmio sem assinatura"
            ]
        },
        {
            keywords: [["pcd"], ["enquadrar", "pcd"]],
            answer: "Para questões de enquadramento como **PCD** (Pessoa com Deficiência), é preciso entrar em contato diretamente com a **Perícia Médica do Estado**."
        },
        {
            keywords: [["assinatura", "contrato"], ["assinar", "contrato"]],
            answer: "Nós não realizamos atendimentos relacionados a **assinatura de contrato**. Para obter suporte e orientações, você deve entrar em contato com o setor de **Gerência de Política e Regulação do Trabalho** através do WhatsApp: **(81) 3184-0331**."
        },
        {
            keywords: [["emitir", "holerite"], ["emitir", "contracheque"], ["acesso", "holerite"], ["acesso", "contracheque"], ["holerite"]],
            answer: "Para acessar ou emitir seu **contracheque (holerite)**, vá ao site **www.nps.pe.gov.br** e faça login com seu CPF e senha. Selecione a seção 'Pagamentos' (ou similar) e escolha o mês desejado para download. Se for seu primeiro acesso, o portal oferece a opção de criar uma senha."
        },
        {
            keywords: [["sassepe"], ["plano", "sassepe"], ["adesao", "sassepe"]],
            answer: "Demandas sobre o **SASSEPE** (como adesão ao plano ou dúvidas) devem ser tratadas **diretamente com o SASSEPE**. Você pode obter mais informações ou acessar os serviços através do site oficial: **www.iassepe.pe.gov.br/sassepe**."
        },
        {
            keywords: [["ficha", "funcional"], ["ficha"]],
            answer: "Para solicitar a **Ficha Funcional**, é preciso preencher o **Requerimento A**."
        },
        {
            keywords: [["plantao", "extra"], ["informe", "rendimento", "plantao"]],
            answer: "Para solicitar informes de rendimento ou tratar assuntos referentes a **Plantão Extra**, você deve **dar entrada diretamente na sua Unidade**."
        },
        {
            keywords: [["enfsus"], ["problema", "enfsus"]],
            answer: "Para resolver problemas de acesso ou qualquer demanda relacionada ao sistema **ENFSUS**, você precisa **procurar a sua Unidade**."
        },
        {
            keywords: [["licenca", "sem", "vencimento"]],
            answer: "A licença sem vencimentos possui caráter **discricionário**. Isso significa que a solicitação será analisada pela gestão da unidade hospitalar, que pode deferir ou indeferir o pedido. Orientamos que você reapresente a solicitação com uma **justificativa clara e detalhada**, acompanhada de toda a **documentação comprobatória** possível, para subsidiar a nova análise da gestão."
        },
        {
            keywords: [["conversao", "tempo", "especial"], ["tempo", "especial"]],
            answer: "Para solicitar a **Conversão de Tempo Especial para Comum**, você deve preencher o **Requerimento A**."
        },
        {
            keywords: [["anotacao", "diploma"], ["diploma"]],
            answer: "Para solicitar **Anotação de Diploma**, você deve preencher o **Requerimento A** e marcar a **Opção 7**."
        },
        {
            keywords: [["perigo", "laboral"], ["erigo", "laboral"], ["pagamento", "laboral"], ["risco", "laboral"]],
            answer: "Para verificar questões sobre não recebimento ou pagamento do **Perigo Laboral**, é preciso preencher o **Requerimento A**."
        },
        {
            keywords: [["vinculo", "aberto"], ["ex", "servidora", "vinculo"]],
            answer: "Caso você seja um ex-servidor e o seu **vínculo continua em aberto**, é preciso preencher o **Requerimento A** para solicitar a regularização."
        },
        {
            keywords: [["vinculo", "prefeitura"], ["declaracao", "vinculo", "prefeitura"]],
            answer: "Nós **não atendemos** demandas referentes a emissão de declaração de vínculo com a **Prefeitura**."
        },
        {
            keywords: [["publicacao", "processo"], ["sei", "externo"], ["cadastro", "sei"], ["acesso", "sei"]],
            answer: "Para acompanhar a publicação e tramitação do seu processo, você pode solicitar acesso ao **SEI Externo**.\nPara liberar o cadastro:\n1. Preencha o formulário em https://sei.pe.gov.br/sei/controlador_externo.php?acao=usuario_externo_logar&id_orgao_acesso_externo=17 clicando em \"Clique aqui para se cadastrar\".\n2. Envie para o e-mail **suporte.sei@sad.pe.gov.br**: Comprovante de residência; RG e CPF; Termo de Declaração de Concordância e Veracidade assinado.\n\nVocê também pode consultar o **Diário Oficial** pelo link: https://diariooficial.cepe.com.br/diariooficialweb"
        },
        {
            keywords: [["valores", "enfsus"], ["valor", "enfsus"]],
            answer: "Para questões referentes a **valores do ENFSUS**, você deve preencher o **Requerimento A** diretamente na sua **unidade**."
        },
        {
            keywords: [["declaracao", "experiencia", "profissional"], ["experiencia", "profissional"]],
            answer: "Para comprovação de **Experiência Profissional**, o documento correto que emitimos é a **Declaração de Vínculo**."
        },
        {
            keywords: [["terceiros", "processo"], ["esposa", "processo"], ["marido", "processo"], ["andamento", "sem", "procuracao"], ["procuracao"]],
            answer: "Para repassar andamento de processo ou informações funcionais para terceiros (esposa, marido, filhos, etc.), é **obrigatória a apresentação de procuração**. Sem procuração, não é possível fornecer as informações."
        },
        {
            keywords: [["afastada", "inss"], ["afastado", "inss"], ["inss", "pedindo", "declaracao"], ["declaracao", "inss"]],
            answer: "Se você está afastado(a) pelo INSS e eles estão pedindo uma declaração, você deve preencher o **Requerimento A** solicitando uma **Declaração de Vínculo**."
        },
        {
            keywords: [["repasse", "enfermagem"], ["nao", "recebeu", "repasse"], ["falta", "repasse"]],
            answer: "Caso não tenha recebido o repasse da enfermagem, é preciso preencher o **Requerimento A**."
        },
        {
            keywords: [["renovar", "contrato"], ["duvida", "contrato", "trabalho"], ["duvidas", "contrato"]],
            answer: "Para renovar ou tirar dúvidas sobre o seu contrato de trabalho, informamos que é preciso procurar ou entrar em contato com a **gestão de trabalho da sua unidade**."
        },
        {
            keywords: [["revisao", "valores"], ["revisao", "valor"]],
            answer: "Para solicitar a revisão de valores, você deve preencher o **Requerimento A**."
        },
        {
            keywords: [["ctc", "fusam"], ["tempo", "fusam"]],
            answer: "Para dar entrada numa CTC do tempo da FUSAM, você deve preencher o **Requerimento FUNAPE de CTC**."
        },
        {
            keywords: [["troca", "cargo", "carteira", "digital"], ["cargo", "carteira", "digital"], ["carteira", "digital"]],
            answer: "Para solicitar a troca de cargo na carteira digital, é preciso preencher o **Requerimento A**."
        },
        {
            keywords: [["aposentadoria", "especial", "saude"], ["aposentadoria", "especial", "valia"]],
            answer: "Sim, a aposentadoria especial já é válida para a área da saúde, **desde que sejam atendidos alguns requisitos**."
        },
        {
            keywords: [["requerimento", "cada", "vinculo"]],
            answer: "Sim, é necessário preencher **um requerimento para cada vínculo**."
        },
        {
            keywords: [["reduzir", "carga", "horaria", "pericia"], ["pericia", "carga", "horaria"], ["como", "reduzir", "carga", "horaria"]],
            answer: "A redução da carga horária apenas é possível **depois de passar por uma perícia médica**."
        },
        {
            keywords: [["remocao", "voltar"], ["pediu", "remocao", "voltar"]],
            answer: "Se você pediu remoção mas gostaria de voltar, informamos que essa demanda é resolvida **diretamente na sua Gestão de Pessoas**."
        },
        {
            keywords: [["dtc", "ativa"], ["dtc", "ativo"]],
            answer: "Como você ainda está na ativa, **não será possível dar entrada em DTC**. Isso é feito somente quando o contrato acabar."
        },
        {
            keywords: [["assinar", "comprovante", "vinculo"]],
            answer: "Não, não é necessário que ninguém assine o seu comprovante de vínculo."
        },
        {
            keywords: [["remocao", "problemas", "saude"], ["remocao", "saude"], ["remocao", "doenca"]],
            answer: "Para solicitar remoção por problemas de saúde, você deve dar entrada no **Requerimento A**, apresentando o **laudo médico do Estado**."
        },
        {
            keywords: [["aposentadoria", "integral"], ["entrada", "aposentadoria", "integral"]],
            answer: "Para solicitar a aposentadoria integral, você deve preencher o **Requerimento FUNAPE**, a **Opção de Regra de Aposentadoria** e a **Declaração de Residência**."
        },
        {
            keywords: [["licenca", "sem", "vencimento", "aposentadoria"], ["licenca", "aposentadoria"]],
            answer: "Não é possível dar entrada em licença sem vencimento enquanto se pede aposentadoria. O motivo é que, mesmo com tempo de contribuição e idade, a licença sem vencimento iria gerar vacância."
        },
        {
            keywords: [["afastar", "acompanhar", "marido"], ["afastar", "acompanhar", "familiar"], ["tratamento", "oncologico"]],
            answer: "Você deve buscar a **chefia imediata da sua unidade** para tratar da possibilidade de afastamento para acompanhamento de familiar, bem como receber a orientação para o **agendamento da perícia médica**."
        },
        {
            keywords: [["colocar", "filho", "sassepe"], ["colocar", "filha", "sassepe"], ["adicionar", "dependente", "sassepe"], ["retirar", "dependente", "sassepe"], ["cancelar", "sassepe"]],
            answer: "Para adicionar ou retirar dependentes, bem como para cancelar o SASSEPE, você deverá entrar em contato diretamente com o próprio SASSEPE, por meio do site: **www.iassepe.pe.gov.br/sassepe**."
        },
        {
            keywords: [["mudanca", "regime"], ["diarista", "plantao"], ["mudar", "plantao"]],
            answer: "Para solicitar a mudança de regime (ex: de diarista para plantão), é necessário procurar o **setor de Recursos Humanos (RH) da sua unidade de lotação** e formalizar a solicitação por meio do **Requerimento A**. A demanda será encaminhada para análise do setor responsável."
        },
        {
            keywords: [["atestado", "beneficio"], ["medico", "varios", "dias", "beneficio"], ["entrar", "beneficio"]],
            answer: "Nesse caso, será necessário procurar o setor de Recursos Humanos (RH) da sua unidade, a fim de obter informações mais precisas sobre a demanda."
        }
    ];

    function getLocalAnswer(message) {
        // Normaliza a string para letras minúsculas e remove acentos
        const msg = message.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        
        let bestMatch = null;
        let maxKeywords = 0;

        for (const item of LOCAL_KNOWLEDGE) {
            for (const condition of item.keywords) {
                const match = condition.every(kw => {
                    const cleanKw = kw.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                    return msg.includes(cleanKw);
                });
                if (match) {
                    // Pega o match mais específico (com mais palavras-chave)
                    if (condition.length > maxKeywords) {
                        maxKeywords = condition.length;
                        bestMatch = item;
                    }
                }
            }
        }
        return bestMatch;
    }

    window.SAS.ai.init = () => {
        // O assistente de IA agora está liberado para todos os usuários

        // Prevent multiple initializations
        if (document.getElementById('sas-ai-container')) return;

        // Restore state from localStorage
        let messageHistory = JSON.parse(localStorage.getItem('sas_ai_history')) || [];
        let isChatOpen = localStorage.getItem('sas_ai_open') === 'true';

        const container = document.createElement('div');
        container.id = 'sas-ai-container';
        container.className = 'fixed bottom-6 right-6 z-[10000] font-sans';

        container.innerHTML = `
            <!-- Chat Bubble Button -->
            <button id="ai-bubble" class="bg-blue-600 hover:bg-blue-700 text-white w-14 h-14 rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 group relative">
                <i data-lucide="sparkles" class="w-6 h-6 animate-pulse"></i>
                <span class="absolute -top-1 -right-1 flex h-3 w-3">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-3 w-3 bg-yellow-500"></span>
                </span>
            </button>

            <!-- Chat Window -->
            <div id="ai-window" class="${isChatOpen ? '' : 'hidden'} absolute bottom-20 right-0 w-[350px] max-w-[90vw] h-[500px] bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden animate-fade-in origin-bottom-right">
                <!-- Header -->
                <div class="bg-blue-600 p-4 flex justify-between items-center text-white">
                    <div class="flex items-center gap-2">
                        <div class="bg-white/20 p-1.5 rounded-lg">
                            <i data-lucide="bot" class="w-5 h-5 text-white"></i>
                        </div>
                        <span class="font-bold">${CHAT_TITLE}</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <button id="ai-sound" style="display:none" class="hover:bg-white/20 p-1.5 rounded-lg transition-colors border border-white/20" title="Áudio Ativado">
                            <i data-lucide="volume-2" class="w-4 h-4 text-white"></i>
                        </button>
                        <button id="ai-clear" class="hover:bg-white/20 p-1.5 rounded-lg transition-colors border border-white/20" title="Limpar conversa">
                            <i data-lucide="trash-2" class="w-4 h-4 text-white"></i>
                        </button>
                        <button id="ai-close" class="hover:bg-white/20 p-1 rounded-lg transition-colors">
                            <i data-lucide="x" class="w-5 h-5"></i>
                        </button>
                    </div>
                </div>

                <!-- Messages area -->
                <div id="ai-messages" class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
                    <div class="flex gap-2 initial-message">
                        <div class="bg-white p-3 rounded-2xl rounded-tl-none shadow-sm border border-slate-100 text-sm text-slate-700 max-w-[85%]">
                            ${WELCOME_MSG}
                        </div>
                    </div>
                </div>

                <!-- Input area -->
                <div class="p-4 bg-white border-t border-slate-100 flex gap-2 items-center">
                    <button id="ai-mic" style="display:none" class="bg-gray-100 text-gray-600 p-2.5 rounded-xl hover:bg-gray-200 transition-colors shadow-sm focus:outline-none" title="Falar">
                        <i data-lucide="mic" class="w-5 h-5"></i>
                    </button>
                    <input type="text" id="ai-input" placeholder="Pergunte algo..." class="flex-1 min-w-0 bg-slate-100 border-none rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 transition-all outline-none">
                    <button id="ai-send" class="bg-blue-600 text-white p-2.5 rounded-xl hover:bg-blue-700 transition-colors shadow-lg shadow-blue-100 focus:outline-none">
                        <i data-lucide="send" class="w-5 h-5"></i>
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(container);
        if (window.lucide) window.lucide.createIcons();

        const bubble = document.getElementById('ai-bubble');
        const windowEl = document.getElementById('ai-window');
        const closeBtn = document.getElementById('ai-close');
        const clearBtn = document.getElementById('ai-clear');
        const soundBtn = document.getElementById('ai-sound');
        const micBtn = document.getElementById('ai-mic');
        const input = document.getElementById('ai-input');
        const sendBtn = document.getElementById('ai-send');
        const messagesArea = document.getElementById('ai-messages');

        let isSoundOn = true;

        const speakText = (text) => {
            if (!window.speechSynthesis || !isSoundOn) return;
            window.speechSynthesis.cancel();

            const cleanText = text.replace(/\*\*/g, '').replace(/\*/g, '').replace(/_/g, '').replace(/#/g, '');
            const utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.lang = 'pt-BR';
            utterance.rate = 1.05;

            const voices = window.speechSynthesis.getVoices();
            const ptVoice = voices.find(v => v.lang === 'pt-BR' && (v.name.includes('Google') || v.name.includes('Luciana') || v.name.includes('Maria')));
            if (ptVoice) utterance.voice = ptVoice;

            window.speechSynthesis.speak(utterance);
        };

        if (window.speechSynthesis) {
            window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
        }

        soundBtn.addEventListener('click', () => {
            isSoundOn = !isSoundOn;
            const icon = soundBtn.querySelector('i');
            if (isSoundOn) {
                icon.setAttribute('data-lucide', 'volume-2');
                soundBtn.title = "Áudio Ativado";
            } else {
                icon.setAttribute('data-lucide', 'volume-x');
                soundBtn.title = "Áudio Desativado";
                window.speechSynthesis.cancel();
            }
            if (window.lucide) window.lucide.createIcons();
        });

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = null;
        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.lang = 'pt-BR';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onstart = () => {
                micBtn.classList.remove('bg-gray-100', 'text-gray-600');
                micBtn.classList.add('bg-red-500', 'text-white', 'animate-pulse');
                input.placeholder = "Ouvindo...";
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                input.value = transcript;
                handleSend(transcript);
            };

            recognition.onerror = (event) => {
                console.error("Speech Error:", event.error);
                resetMicUI();
                if (event.error === 'not-allowed' || event.error === 'security') {
                    alert("Microfone bloqueado pelo Chrome! Se este site não tiver HTTPS (Cadeado fechado) ou não for localhost, o Chrome impede o uso da voz por segurança.");
                } else if (event.error === 'network') {
                    alert("Erro de rede: O Chrome não conseguiu conectar ao provedor de voz do Google.");
                } else {
                    alert("Erro no reconhecimento de voz: " + event.error);
                }
            };

            recognition.onend = () => {
                resetMicUI();
            };
        } else {
            micBtn.style.display = 'none';
        }

        function resetMicUI() {
            micBtn.classList.remove('bg-red-500', 'text-white', 'animate-pulse');
            micBtn.classList.add('bg-gray-100', 'text-gray-600');
            input.placeholder = "Pergunte algo...";
        }

        micBtn.addEventListener('click', () => {
            if (recognition) {
                recognition.start();
            } else {
                alert("Seu navegador não suporta reconhecimento de voz. Tente usar o Google Chrome.");
            }
        });

        const saveState = () => {
            localStorage.setItem('sas_ai_history', JSON.stringify(messageHistory));
            localStorage.setItem('sas_ai_open', !windowEl.classList.contains('hidden'));
        };

        const toggleChat = () => {
            const isHidden = windowEl.classList.contains('hidden');
            if (isHidden) {
                windowEl.classList.remove('hidden');
                input.focus();
                // Ensure it's scrolled to bottom instantly when opening
                messagesArea.scrollTop = messagesArea.scrollHeight;
                setTimeout(() => {
                    messagesArea.scrollTop = messagesArea.scrollHeight;
                }, 10);
            } else {
                windowEl.classList.add('hidden');
            }
            saveState();
        };

        const addMessage = (text, isUser = false, save = true, messageId = null) => {
            const msgDiv = document.createElement('div');
            msgDiv.className = isUser ? 'flex justify-end' : 'flex flex-col gap-1';

            const currentId = messageId || 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

            const innerDiv = document.createElement('div');
            innerDiv.className = isUser
                ? 'bg-blue-600 text-white p-3 rounded-2xl rounded-tr-none shadow-md text-sm max-w-[85%]'
                : 'bg-white p-3 rounded-2xl rounded-tl-none shadow-sm border border-slate-100 text-sm text-slate-700 max-w-[85%] relative group';

            // Handle markdown-ish bold and line breaks
            innerDiv.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');

            msgDiv.appendChild(innerDiv);

            // Add Feedback Buttons only for bot messages (except the very first welcome msg if we don't want to)
            if (!isUser && text !== WELCOME_MSG) {
                const feedbackDiv = document.createElement('div');
                feedbackDiv.className = 'flex gap-2 text-xs ml-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200';
                feedbackDiv.innerHTML = `
                    <button class="feedback-btn hover:text-blue-600 transition-colors flex items-center gap-1 text-slate-400" data-id="${currentId}" data-type="positive" title="Resposta útil">
                        <i data-lucide="thumbs-up" class="w-3 h-3"></i> Útil
                    </button>
                    <button class="feedback-btn hover:text-red-600 transition-colors flex items-center gap-1 text-slate-400" data-id="${currentId}" data-type="negative" title="Resposta ruim">
                        <i data-lucide="thumbs-down" class="w-3 h-3"></i>
                    </button>
                    <span class="feedback-ack hidden text-green-600 italic">Obrigado!</span>
                `;

                feedbackDiv.querySelectorAll('.feedback-btn').forEach(btn => {
                    btn.addEventListener('click', async (e) => {
                        const isPositive = btn.dataset.type === 'positive';
                        const ack = feedbackDiv.querySelector('.feedback-ack');

                        // Visual feedback instantly
                        feedbackDiv.querySelectorAll('.feedback-btn').forEach(b => b.classList.add('hidden'));
                        ack.classList.remove('hidden');

                        try {
                            // Find the last user message for context
                            let lastUserMsg = "";
                            for (let i = messageHistory.length - 1; i >= 0; i--) {
                                if (messageHistory[i].role === 'user') {
                                    lastUserMsg = messageHistory[i].content;
                                    break;
                                }
                            }

                            await fetch('/api/ai/feedback', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    message_id: currentId,
                                    is_positive: isPositive,
                                    feedback: '',
                                    original_message: lastUserMsg,
                                    ai_response: text
                                })
                            });
                        } catch (err) {
                            console.error('Feedback error:', err);
                        }
                    });
                });

                // We wrap innerDiv and feedbackDiv in a horizontal flex to align them, or just append below
                // Since msgDiv is 'flex-col' for bot, appending it below is fine
                msgDiv.appendChild(feedbackDiv);
                // Important: we need to add the group class to msgDiv instead of innerDiv so hover works
                msgDiv.classList.add('group');
                innerDiv.classList.remove('group');
            }

            if (save) {
                // Update history (keep last 10 messages)
                messageHistory.push({ role: isUser ? 'user' : 'model', content: text, id: currentId });
                if (messageHistory.length > 10) messageHistory.shift();
                saveState();
            }

            // Remove and re-add suggestions only if it's the latest bot message
            const suggestions = document.getElementById('ai-suggestions');
            if (suggestions) suggestions.remove();

            messagesArea.appendChild(msgDiv);
            messagesArea.scrollTop = messagesArea.scrollHeight;
        };

        // Restore history visually
        if (messageHistory.length > 0) {
            messageHistory.forEach(msg => addMessage(msg.content, msg.role === 'user', false, msg.id));
            // Final scroll to bottom instantly after all messages are added
            messagesArea.scrollTop = messagesArea.scrollHeight;
            setTimeout(() => {
                messagesArea.scrollTop = messagesArea.scrollHeight;
            }, 50);
        } else {
            // Add suggestions if no history
            const sugDiv = document.createElement('div');
            sugDiv.id = 'ai-suggestions';
            sugDiv.className = 'flex flex-wrap gap-2 pt-2';
            sugDiv.innerHTML = QUICK_QUESTIONS.map(q => `
                <button class="suggestion-btn text-[11px] bg-blue-50 text-blue-700 border border-blue-100 px-3 py-1.5 rounded-full hover:bg-blue-600 hover:text-white transition-all">
                    ${q}
                </button>
            `).join('');
            messagesArea.appendChild(sugDiv);
            sugDiv.querySelectorAll('.suggestion-btn').forEach(btn => {
                btn.addEventListener('click', () => handleSend(btn.textContent.trim()));
            });
        }

        const clearChat = () => {
            messageHistory = [];
            saveState();
            messagesArea.innerHTML = `
                <div class="flex gap-2 initial-message">
                    <div class="bg-white p-3 rounded-2xl rounded-tl-none shadow-sm border border-slate-100 text-sm text-slate-700 max-w-[85%]">
                        ${WELCOME_MSG}
                    </div>
                </div>
                <div class="flex flex-wrap gap-2 pt-2" id="ai-suggestions">
                    ${QUICK_QUESTIONS.map(q => `
                        <button class="suggestion-btn text-[11px] bg-blue-50 text-blue-700 border border-blue-100 px-3 py-1.5 rounded-full hover:bg-blue-600 hover:text-white transition-all">
                            ${q}
                        </button>
                    `).join('')}
                </div>
            `;
            messagesArea.querySelectorAll('.suggestion-btn').forEach(btn => {
                btn.addEventListener('click', () => handleSend(btn.textContent.trim()));
            });
        };

        const handleSend = async (text = null) => {
            const message = text || input.value.trim();
            if (!message) return;

            addMessage(message, true);
            input.value = '';

            const typingDiv = document.createElement('div');
            typingDiv.className = 'flex gap-2 animate-pulse';
            typingDiv.id = 'ai-typing';
            typingDiv.innerHTML = `
                <div class="bg-white p-3 rounded-2xl rounded-tl-none shadow-sm border border-slate-100 text-xs text-slate-400">
                    Digitando...
                </div>
            `;
            messagesArea.appendChild(typingDiv);
            messagesArea.scrollTop = messagesArea.scrollHeight;

            const localItem = getLocalAnswer(message);
            if (localItem) {
                setTimeout(() => {
                    typingDiv.remove();
                    
                    if (localItem.answer) {
                        addMessage(localItem.answer);
                    }
                    
                    if (localItem.options && localItem.options.length > 0) {
                        const questionMsg = localItem.question || "Por favor, seja mais específico. Qual destas opções você deseja?";
                        addMessage(questionMsg);
                        
                        // Adiciona as sugestões (botões clicáveis)
                        const sugDiv = document.createElement('div');
                        sugDiv.className = 'flex flex-wrap gap-2 pt-2 mb-4';
                        sugDiv.innerHTML = localItem.options.map(q => `
                            <button class="suggestion-btn text-[11px] bg-blue-50 text-blue-700 border border-blue-100 px-3 py-1.5 rounded-full hover:bg-blue-600 hover:text-white transition-all">
                                ${q}
                            </button>
                        `).join('');
                        messagesArea.appendChild(sugDiv);
                        messagesArea.scrollTop = messagesArea.scrollHeight;
                        
                        sugDiv.querySelectorAll('.suggestion-btn').forEach(btn => {
                            btn.addEventListener('click', () => handleSend(btn.textContent.trim()));
                        });
                    }

                    if (window.lucide) window.lucide.createIcons();
                }, 600);
                return;
            }

            let userContextStr = "";
            try {
                const currentUser = JSON.parse(localStorage.getItem('sas_user'));
                if (currentUser) {
                    userContextStr = JSON.stringify({
                        id: currentUser.id,
                        nome: currentUser.nome_completo,
                        tipo: currentUser.tipo
                    });
                }
            } catch (e) { }

            try {
                const response = await fetch('/api/ai/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message,
                        history: messageHistory.map(m => ({ role: m.role, content: m.content })),
                        user_context: userContextStr
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    typingDiv.remove();
                    addMessage(data.reply);
                    // speakText(data.reply); // [VOZ DESATIVADA] Descomentar para reativar junto com os botões de mic e volume
                    if (window.lucide) window.lucide.createIcons();
                } else {
                    throw new Error();
                }
            } catch (e) {
                typingDiv.remove();
                addMessage("Desculpe, estou com dificuldade de conexão agora. Tente de novo em alguns instantes!");
                if (window.lucide) window.lucide.createIcons();
            }
        };

        bubble.addEventListener('click', () => { toggleChat(); if (window.lucide) window.lucide.createIcons(); });
        closeBtn.addEventListener('click', toggleChat);
        clearBtn.addEventListener('click', clearChat);
        sendBtn.addEventListener('click', () => handleSend());
        input.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleSend(); });
    };
})();
