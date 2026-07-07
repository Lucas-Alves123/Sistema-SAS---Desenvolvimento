/**
 * SAS - PDF Generator
 * Responsável por gerar o Requerimento A oficial (2 páginas) e o Comprovante de Atendimento.
 */

window.SAS = window.SAS || {};
window.SAS.pdf = {
    
    // Lista de itens do Requerimento A conforme imagem oficial (1 a 33)
    requerItems: [
        "AFASTAMENTO P/ PÓS-GRADUAÇÃO (DOUT, MEST, ESPEC.)",
        "AFASTAMENTO P/ CURSOS - CONGRESSOS (NACIONAL / EXTERIOR)",
        "ANOTAÇÃO DE DIPLOMAS / CERTIFICADO DE CURSO",
        "REMOÇÃO OU TRANSFERÊNCIA",
        "EXONERAÇÃO (CARGO EFETIVO, C. COM. ) DISPENSA (FUN. GRAT )",
        "RESCISÃO DE CONTRATO",
        "PROMOÇÃO POR TITULAÇÃO",
        "INCENTIVO À TITULAÇÃO",
        "LICENÇA P/ TRATO INTERESSE PART. (S/ VENCIMENTOS)",
        "LICENÇAS (GESTÃO, TRAT. DE SAÚDE, DE DÇA DE FAMILIARES)",
        "LICENÇA PARA ACOMPANHAR CÔNJUGE",
        "DEDICAÇÃO EXCLUSIVA - DE",
        "RETIFICAÇÃO DE NOME",
        "READAPTAÇÃO DE FUNÇÃO",
        "ABONO PERMANÊNCIA",
        "SALÁRIO FAMÍLIA",
        "RISCO DE VIDA",
        "REVISÃO DE SITUAÇÃO FUNCIONAL",
        "CONTAGEM DE TEMPO DE SERVIÇO",
        "CERTIDÃO PARA FINS ESPECÍFICOS",
        "AVERBAÇÃO DE TEMPO DE SERVIÇO",
        "DESAVERBAÇÃO DE TEMPO DE SERVIÇO",
        "ALTERAÇÃO DE CARGA HORÁRIA",
        "ANTECIPAÇÃO DO 13º SALÁRIO",
        "AUXÍLIO CRECHE",
        "AUXÍLIO EDUCAÇÃO",
        "AUXÍLIO FUNERAL",
        "AUXÍLIO PARA COMPRA DE MATERIAL ESCOLAR",
        "PPP/LTCAT",
        "PNE - AUXÍLIO NECESSIDADES ESPECIAIS",
        "ABONO DE FALTA PERÍODO: ___/___/___ A ___/___/___",
        "OUTROS: CITAR",
        "LICENÇA PRÊMIO   [   ] CONCESSÃO  [   ] GOZO"
    ],

    /**
     * Gera o PDF do Requerimento A Oficial (Fiel à Imagem)
     */
    generateRequerimentoA: async (ag) => {
        // Se ag for uma string ou número (ID), busca os dados completos no backend
        let agObj = ag;
        if (ag && (typeof ag === 'string' || typeof ag === 'number')) {
            try {
                agObj = await window.SAS.base44.entities.Agendamento.get(ag);
            } catch (e) {
                console.error("Erro ao carregar agendamento:", e);
                window.SAS.utils.notify('error', 'Erro ao carregar dados do atendimento.');
                return;
            }
        }
        
        // Abre o modal de edição antes de gerar o PDF
        window.SAS.pdf.openEditModal(agObj || {});
    },

    /**
     * Gera o PDF com as informações editadas
     */
    generateRequerimentoAPDF: async (ag, customData = null) => {
        let reqData = {};
        if (customData) {
            reqData = customData;
        } else if (ag && ag.requerimento_a_data) {
            try {
                reqData = typeof ag.requerimento_a_data === 'string' ? JSON.parse(ag.requerimento_a_data) : ag.requerimento_a_data;
            } catch (e) { console.error("Error parsing requerimento_a_data", e); }
        }

        const getVal = (key, fallback = '') => {
            return (reqData[key] !== undefined && reqData[key] !== null) ? reqData[key] : (fallback || '');
        };

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        const marginX = 15;
        let y = 15;

        // --- CABEÇALHO ---
        try {
            const imgGov = await window.SAS.pdf.getBase64Image('../images/govpe.png');
            // Logo maior e mais alta (x centralizado: (210-55)/2 = 77.5)
            doc.addImage(imgGov, 'PNG', 77.5, 5, 55, 30);
        } catch (e) { console.warn("Logo GovPE não carregada"); }

        doc.setFont("helvetica", "bold");
        doc.setFontSize(13);
        doc.text("SECRETARIA ESTADUAL DE SAÚDE DE PERNAMBUCO", 105, 38, { align: "center" });
        
        y = 44;

        // --- TABELA 1: REQUERIMENTO TÍTULO ---
        doc.setFillColor(230, 230, 230);
        doc.rect(marginX, y, 180, 7, 'F');
        doc.rect(marginX, y, 180, 7, 'S');
        doc.setFontSize(10);
        doc.text("R E Q U E R I M E N T O", 105, y + 5, { align: "center" });
        y += 7;

        // --- GRID DE IDENTIFICAÇÃO ---
        doc.setFontSize(7);
        const rowH = 6.3;
        
        // R1: NOME
        doc.rect(marginX, y, 180, rowH);
        doc.text(`NOME: ${getVal('nome_completo', ag.nome_completo)}`, marginX + 2, y + 4.5); y += rowH;

        // R2: NOME SOCIAL
        doc.rect(marginX, y, 180, rowH);
        doc.text(`NOME SOCIAL: ${getVal('nome_social', '')}`, marginX + 2, y + 4.5); y += rowH;

        // R3: CARGO / CLASSE / MATRICULA / VINCULO
        doc.rect(marginX, y, 65, rowH); doc.text(`CARGO/FUNÇÃO: ${getVal('cargo', ag.cargo)}`, marginX + 2, y + 4.5);
        doc.rect(marginX + 65, y, 50, rowH); doc.text(`CLASSE/NÍVEL/TITULAÇÃO: ${getVal('classe', '')}`, marginX + 66, y + 4.5);
        doc.rect(marginX + 115, y, 35, rowH); doc.text(`MATRÍCULA: ${getVal('matricula', ag.matricula)}`, marginX + 116, y + 4.5);
        doc.rect(marginX + 150, y, 30, rowH); doc.text(`VÍNCULO: ${getVal('vinculo', ag.vinculo)}`, marginX + 151, y + 4.5);
        y += rowH;

        // R4: CPF / RG / ORGAO / UF
        doc.rect(marginX, y, 65, rowH * 2); doc.text(`CPF: ${getVal('cpf', ag.cpf)}`, marginX + 2, y + 5);
        doc.rect(marginX + 65, y, 50, rowH * 2); doc.text(`RG: ${getVal('rg', '')}`, marginX + 66, y + 5);
        doc.rect(marginX + 115, y, 35, rowH * 2); doc.text(`ÓRGÃO\nEXPEDIDOR: ${getVal('orgao_expedidor', '')}`, marginX + 116, y + 5);
        doc.rect(marginX + 150, y, 30, rowH * 2); doc.text(`UF: ${getVal('uf_expedidor', '')}`, marginX + 151, y + 5);
        y += (rowH * 2);

        // R5: LOTAÇÃO / ADMISSÃO / CH
        doc.rect(marginX, y, 120, rowH * 2); doc.text(`ÓRGÃO DE LOTAÇÃO: ${getVal('local_trabalho', ag.local_trabalho)}`, marginX + 2, y + 6);
        doc.rect(marginX + 120, y, 35, rowH * 2); doc.text(`DATA\nADMISSÃO: ${getVal('data_admissao', '')}`, marginX + 121, y + 5.5);
        doc.rect(marginX + 155, y, 25, rowH * 2); doc.text(`C.H.: ${getVal('carga_horaria', '')}`, marginX + 156, y + 6);
        y += (rowH * 2);

        // R6: EMAIL / NO. / APT
        doc.rect(marginX, y, 120, rowH); doc.text(`EMAIL: ${getVal('email', ag.email)}`, marginX + 2, y + 4.5);
        doc.rect(marginX + 120, y, 35, rowH); doc.text(`Nº.: ${getVal('numero_endereco', '')}`, marginX + 121, y + 4.5);
        doc.rect(marginX + 155, y, 25, rowH); doc.text(`APT: ${getVal('apartamento_endereco', '')}`, marginX + 156, y + 4.5);
        y += rowH;

        // R7: TEL SETOR / TEL RESID / TEL CEL
        doc.rect(marginX, y, 65, rowH * 2); doc.text(`TELEFONE SETOR/UNIDADE:\n${getVal('telefone_setor', '')}`, marginX + 2, y + 5);
        doc.rect(marginX + 65, y, 55, rowH * 2); doc.text(`TELEFONE RESIDENCIAL:\n${getVal('telefone_residencial', '')}`, marginX + 66, y + 5);
        doc.rect(marginX + 120, y, 60, rowH * 2); doc.text(`TELEFONE CELULAR:\n${getVal('telefone_celular', ag.telefone)}`, marginX + 121, y + 5);
        y += (rowH * 2);

        // R8: ENDEREÇO / NO / BAIRRO
        doc.rect(marginX, y, 120, rowH); doc.text(`ENDEREÇO: ${getVal('endereco', '')}`, marginX + 2, y + 4.5);
        doc.rect(marginX + 120, y, 35, rowH); doc.text(`Nº: ${getVal('numero_residencial', '')}`, marginX + 121, y + 4.5);
        doc.rect(marginX + 155, y, 25, rowH); doc.text(`BAIRRO: ${getVal('bairro', '')}`, marginX + 156, y + 4.5);
        y += rowH;

        // R9: COMPLEMENTO / CIDADE / UF / CEP
        doc.rect(marginX, y, 65, rowH); doc.text(`COMPLEMENTO: ${getVal('complemento', '')}`, marginX + 2, y + 4.5);
        doc.rect(marginX + 65, y, 55, rowH); doc.text(`CIDADE: ${getVal('cidade', '')}`, marginX + 66, y + 4.5);
        doc.rect(marginX + 120, y, 35, rowH); doc.text(`UF: ${getVal('uf', '')}`, marginX + 121, y + 4.5);
        doc.rect(marginX + 155, y, 25, rowH); doc.text(`CEP: ${getVal('cep', '')}`, marginX + 156, y + 4.5);
        y += rowH;

        // --- SEÇÃO: REQUER AO ---
        doc.setFillColor(230, 230, 230);
        doc.rect(marginX, y, 180, 8, 'F');
        doc.rect(marginX, y, 180, 8, 'S');
        doc.setFont("helvetica", "bold");
        doc.text("REQUER AO", 105, y + 6, { align: "center" });
        y += 8;

        const checkH = 5.0; // Reduzido para economizar espaço
        const colW = 90;
        doc.setFontSize(6.5);
        
        for (let i = 0; i < 18; i++) {
            const itemL = i + 1;
            const itemR = i + 19;
            
            // Coluna Esquerda (01 a 18)
            window.SAS.pdf.drawCheckItem(doc, marginX, y, itemL, ag, reqData);
            
            // Coluna Direita (Lógica corrigida para evitar sobreposição)
            if (i === 17) {
                 // Caso especial da última linha: DECÊNIO
                 // Bloco Decênio ocupa o espaço do número + checkbox (16mm)
                 doc.rect(marginX + colW, y, 16, checkH);
                 doc.setFont("helvetica", "bold");
                 doc.setFontSize(5.5);
                 doc.text("DECÊNIO", marginX + colW + 1, y + 3.5);
                 
                 // Bloco Período ocupa o restante
                 doc.rect(marginX + colW + 16, y, 74, checkH);
                 doc.setFont("helvetica", "normal");
                 doc.text("PERÍODO: ________/________/________ A ________/________/________", marginX + colW + 18, y + 3.5);
            } else if (itemR <= 33) {
                // Itens 19 a 33
                window.SAS.pdf.drawCheckItem(doc, marginX + colW, y, itemR, ag, reqData);
            } else if (itemR <= 36) {
                // Caixas vazias para as linhas 16 e 17 no lado direito
                const numW = 8;
                const boxW = 8;
                doc.rect(marginX + colW, y, numW, checkH);
                doc.rect(marginX + colW + numW, y, boxW, checkH);
                doc.rect(marginX + colW + numW + boxW, y, 90 - numW - boxW, checkH);
            }
            
            y += checkH;
        }

        // --- INFORMAÇÕES COMPLEMENTARES ---
        doc.setFont("helvetica", "bold");
        doc.setFontSize(7);
        // Caixa de Título
        doc.rect(marginX, y, 180, 10); 
        const titleLine1 = "ESPAÇO RESERVADO PARA REGISTRO DOS DOCUMENTOS ANEXADOS NECESSÁRIOS À INSTRUÇÃO DO PROCESSO";
        const titleLine2 = "E PARA INFORMAÇÕES COMPLEMENTARES.";
        doc.text(titleLine1, 105, y + 4, { align: "center" });
        doc.text(titleLine2, 105, y + 8, { align: "center" });
        y += 10;
        
        const infoBoxH = 18; // Reduzido
        doc.rect(marginX, y, 180, infoBoxH);
        
        // Linhas de escrita (Limpo, sem caracteres extras)
        doc.setDrawColor(200, 200, 200);
        for(let l = 1; l <= 3; l++) {
            doc.line(marginX, y + (l * 5), marginX + 180, y + (l * 5));
        }
        doc.setDrawColor(0, 0, 0);

        doc.setFont("helvetica", "normal");
        
        // Exibir as observações editadas
        const customInfo = getVal('informacoes_complementares', '');
        if (customInfo) {
            doc.setFontSize(6.5);
            const splitObs = doc.splitTextToSize(customInfo, 175);
            doc.text(splitObs, marginX + 2, y + 4);
        }
        
        y += infoBoxH + 4;

        // --- BLOCO DE ASSINATURAS (Protegido contra corte) ---
        doc.setLineWidth(0.4);
        doc.rect(marginX - 2, y - 1, 184, 30); 
        doc.setLineWidth(0.2);
        
        const sigW = 58;
        const sigH = 26;
        const sigGap = 2;
        
        doc.setFontSize(7);
        // 1. Requerente
        doc.rect(marginX, y, sigW, sigH);
        doc.setFont("helvetica", "normal");
        doc.text("Em: ________/________/________", marginX + 4, y + 7);
        doc.line(marginX + 5, y + 18, marginX + sigW - 5, y + 18);
        doc.setFontSize(5.5);
        doc.setFont("helvetica", "bold");
        doc.text("ASSINATURA DO REQUERENTE", marginX + sigW/2, y + 22, { align: "center" });

        // 2. Chefia
        doc.rect(marginX + sigW + sigGap, y, sigW, sigH);
        doc.setFont("helvetica", "normal");
        doc.setFontSize(7);
        doc.text("Em: ________/________/________", marginX + sigW + sigGap + 4, y + 7);
        doc.line(marginX + sigW + sigGap + 5, y + 18, marginX + sigW + sigGap + sigW - 5, y + 18);
        doc.setFontSize(5.5);
        doc.setFont("helvetica", "bold");
        doc.text("ASSINATURA DA CHEFIA IMEDIATA", marginX + sigW + sigGap + sigW/2, y + 22, { align: "center" });

        // 3. Diretor
        doc.rect(marginX + (sigW + sigGap) * 2, y, sigW, sigH);
        doc.setFont("helvetica", "normal");
        doc.setFontSize(7);
        doc.text("Em: ________/________/________", marginX + (sigW + sigGap) * 2 + 4, y + 7);
        doc.line(marginX + (sigW + sigGap) * 2 + 5, y + 18, marginX + (sigW + sigGap) * 2 + sigW - 5, y + 18);
        doc.setFontSize(5.5);
        doc.setFont("helvetica", "bold");
        doc.text("ASSINATURA DO GERENTE / DIRETOR", marginX + (sigW + sigGap) * 2 + sigW/2, y + 22, { align: "center" });

        // Página 2: Esclarecimentos
        doc.addPage();
        window.SAS.pdf.generateEsclarecimentos(doc);

        const pdfName = `Requerimento_A_${(getVal('nome_completo', ag.nome_completo) || 'servidor').trim().replace(/\s+/g, '_')}.pdf`;
        doc.save(pdfName);
    },

    /**
     * Auxiliar para desenhar cada linha do checklist com dados customizados
     */
    drawCheckItem: (doc, x, y, num, ag, reqData = {}) => {
        const h = 5.5;
        const numW = 8;
        const boxW = 8;
        const labelW = 74;

        // Número
        doc.rect(x, y, numW, h);
        doc.setFont("helvetica", "bold");
        doc.text(num.toString().padStart(2, '0'), x + 2.2, y + 4);
        
        // Quadrado (Checkbox)
        doc.rect(x + numW, y, boxW, h);
        
        // Lógica de Marcação (Inteligente com Override)
        let isChecked = false;
        if (reqData && reqData.selected_items !== undefined && reqData.selected_items !== null) {
            isChecked = reqData.selected_items.includes(num);
        } else {
            isChecked = window.SAS.pdf.shouldCheckItem(num, ag);
        }

        if (isChecked) {
            doc.text("X", x + numW + 2.8, y + 4);
        }

        // Descrição
        doc.rect(x + numW + boxW, y, labelW, h);
        doc.setFont("helvetica", "normal");
        doc.setFontSize(6); // Reduzido de 6.5 para 6 para evitar vazamento
        const text = window.SAS.pdf.requerItems[num - 1];
        doc.text(text, x + numW + boxW + 2, y + 3.8);
        doc.setFontSize(7.5);
    },

    /**
     * Abre o modal de preenchimento e edição do Requerimento A
     */
    openEditModal: (ag) => {
        let modal = document.getElementById('requerimentoEditModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'requerimentoEditModal';
            modal.className = 'fixed inset-0 bg-black/60 hidden flex items-center justify-center z-[200] p-4 overflow-y-auto';
            modal.innerHTML = `
                <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl overflow-hidden border border-slate-200 flex flex-col max-h-[90vh] animate-fade-in">
                    <!-- Header -->
                    <div class="bg-gradient-to-r from-blue-700 to-blue-900 p-5 text-white flex justify-between items-center">
                        <div>
                            <h3 class="text-lg font-bold flex items-center gap-2">
                                <i data-lucide="edit-3" class="w-5 h-5"></i>
                                Preencher Requerimento A
                            </h3>
                            <p class="text-xs text-blue-200 mt-1 uppercase tracking-wider font-bold">Edite as informações antes de gerar o PDF</p>
                        </div>
                        <button id="reqEditModalClose" class="p-1.5 hover:bg-white/10 rounded-full transition-colors">
                            <i data-lucide="x" class="w-5 h-5"></i>
                        </button>
                    </div>

                    <!-- Tabs Header -->
                    <div class="flex border-b border-slate-200 bg-slate-50 px-4">
                        <button id="reqTabBtnServidor" class="px-4 py-3 text-sm font-bold text-blue-600 border-b-2 border-blue-600 transition-colors">
                            1. Dados do Servidor
                        </button>
                        <button id="reqTabBtnChecklist" class="px-4 py-3 text-sm font-medium text-slate-500 hover:text-blue-600 transition-colors">
                            2. Checklist (Requer ao)
                        </button>
                        <button id="reqTabBtnComplemento" class="px-4 py-3 text-sm font-medium text-slate-500 hover:text-blue-600 transition-colors">
                            3. Informações Complementares
                        </button>
                    </div>

                    <!-- Body / Form -->
                    <div class="p-6 overflow-y-auto flex-1 bg-white">
                        <!-- Tab 1: Dados do Servidor -->
                        <div id="reqTabContentServidor" class="space-y-4">
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <!-- Group 1: Identificacao -->
                                <div class="col-span-3 border-b border-slate-100 pb-1">
                                    <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Identificação</h4>
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Nome Completo</label>
                                    <input type="text" id="reqInputNome" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Nome Social</label>
                                    <input type="text" id="reqInputNomeSocial" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">CPF</label>
                                    <input type="text" id="reqInputCpf" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">RG</label>
                                    <input type="text" id="reqInputRg" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Órgão Expedidor</label>
                                    <input type="text" id="reqInputOrgaoExp" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">UF Expedidor</label>
                                    <input type="text" id="reqInputUfExp" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>

                                <!-- Group 2: Vida Funcional -->
                                <div class="col-span-3 border-b border-slate-100 pb-1 mt-2">
                                    <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Vida Funcional</h4>
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Cargo/Função</label>
                                    <input type="text" id="reqInputCargo" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Classe/Nível/Titulação</label>
                                    <input type="text" id="reqInputClasse" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Matrícula</label>
                                    <input type="text" id="reqInputMatricula" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Vínculo</label>
                                    <input type="text" id="reqInputVinculo" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Órgão de Lotação</label>
                                    <input type="text" id="reqInputLotacao" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Data de Admissão</label>
                                    <input type="text" id="reqInputAdmissao" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Carga Horária (C.H.)</label>
                                    <input type="text" id="reqInputCh" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>

                                <!-- Group 3: Contato & Endereço -->
                                <div class="col-span-3 border-b border-slate-100 pb-1 mt-2">
                                    <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Contato & Endereço</h4>
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">E-mail</label>
                                    <input type="text" id="reqInputEmail" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Telefone Celular</label>
                                    <input type="text" id="reqInputTelCelular" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Telefone Residencial</label>
                                    <input type="text" id="reqInputTelResidencial" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Telefone Setor/Unidade</label>
                                    <input type="text" id="reqInputTelSetor" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div class="col-span-2">
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Endereço</label>
                                    <input type="text" id="reqInputEndereco" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Nº</label>
                                    <input type="text" id="reqInputEndNumero" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">APT</label>
                                    <input type="text" id="reqInputEndApt" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Bairro</label>
                                    <input type="text" id="reqInputEndBairro" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Cidade</label>
                                    <input type="text" id="reqInputEndCidade" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">UF</label>
                                    <input type="text" id="reqInputEndUf" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">CEP</label>
                                    <input type="text" id="reqInputEndCep" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div class="col-span-2">
                                    <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Complemento</label>
                                    <input type="text" id="reqInputEndComplemento" class="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                            </div>
                        </div>

                        <!-- Tab 2: Checklist (Requer ao) -->
                        <div id="reqTabContentChecklist" class="hidden space-y-4">
                            <p class="text-xs text-slate-500 mb-2">Marque os itens que deseja selecionar para exibição com "X" no checklist do PDF:</p>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2 max-h-[50vh] overflow-y-auto pr-2" id="reqChecklistGrid">
                                <!-- Checkboxes dynamic layout -->
                            </div>
                        </div>

                        <!-- Tab 3: Informações Complementares -->
                        <div id="reqTabContentComplemento" class="hidden space-y-4">
                            <div>
                                <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Informações Complementares / Documentos Anexados</label>
                                <textarea id="reqInputComplemento" rows="6" class="w-full border border-slate-200 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none" placeholder="Digite as informações complementares que serão impressas no campo reservado do requerimento (máx. 3 linhas recomendadas)..."></textarea>
                            </div>
                        </div>
                    </div>

                    <!-- Footer -->
                    <div class="bg-slate-50 border-t border-slate-100 p-4 flex flex-wrap gap-3 justify-end items-center">
                        <button id="reqBtnCancel" class="px-5 py-2 text-sm bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold rounded-lg transition-colors">
                            Cancelar
                        </button>
                        <button id="reqBtnDirect" class="px-5 py-2 text-sm bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg transition-colors flex items-center gap-1.5">
                            <i data-lucide="download" class="w-4 h-4"></i>
                            Gerar PDF sem Salvar
                        </button>
                        <button id="reqBtnSave" class="px-5 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition-colors flex items-center gap-1.5 shadow-md shadow-blue-100">
                            <i data-lucide="save" class="w-4 h-4"></i>
                            Salvar no Sistema e Gerar
                        </button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            // Tab toggles setup
            const tabs = [
                { btn: 'reqTabBtnServidor', content: 'reqTabContentServidor' },
                { btn: 'reqTabBtnChecklist', content: 'reqTabContentChecklist' },
                { btn: 'reqTabBtnComplemento', content: 'reqTabContentComplemento' }
            ];

            tabs.forEach(t => {
                document.getElementById(t.btn).onclick = () => {
                    tabs.forEach(x => {
                        document.getElementById(x.btn).className = 'px-4 py-3 text-sm font-medium text-slate-500 hover:text-blue-600 transition-colors';
                        document.getElementById(x.content).classList.add('hidden');
                    });
                    document.getElementById(t.btn).className = 'px-4 py-3 text-sm font-bold text-blue-600 border-b-2 border-blue-600 transition-colors';
                    document.getElementById(t.content).classList.remove('hidden');
                };
            });

            // Populate checkboxes template
            const checklistGrid = document.getElementById('reqChecklistGrid');
            checklistGrid.innerHTML = window.SAS.pdf.requerItems.map((item, idx) => {
                const itemNum = idx + 1;
                return `
                    <label class="flex items-start gap-3 p-2 bg-slate-50 hover:bg-slate-100 rounded-lg border border-slate-100 cursor-pointer select-none">
                        <input type="checkbox" id="reqChkItem_${itemNum}" class="mt-1 w-4 h-4 rounded text-blue-600 border-slate-300 focus:ring-blue-500">
                        <div class="text-xs text-slate-700">
                            <span class="font-bold text-slate-500">${String(itemNum).padStart(2, '0')}.</span>
                            ${item}
                        </div>
                    </label>
                `;
            }).join('');
        }

        // Parse database values
        let reqData = {};
        if (ag.requerimento_a_data) {
            try {
                reqData = typeof ag.requerimento_a_data === 'string' ? JSON.parse(ag.requerimento_a_data) : ag.requerimento_a_data;
            } catch (e) { console.error("Error parsing saved requerimento_a_data", e); }
        }

        const getVal = (key, fallback = '') => {
            return (reqData[key] !== undefined && reqData[key] !== null) ? reqData[key] : (fallback || '');
        };

        // Populate Form Fields
        document.getElementById('reqInputNome').value = getVal('nome_completo', ag.nome_completo);
        document.getElementById('reqInputNomeSocial').value = getVal('nome_social', '');
        document.getElementById('reqInputCpf').value = getVal('cpf', ag.cpf);
        document.getElementById('reqInputRg').value = getVal('rg', '');
        document.getElementById('reqInputOrgaoExp').value = getVal('orgao_expedidor', '');
        document.getElementById('reqInputUfExp').value = getVal('uf_expedidor', '');
        
        document.getElementById('reqInputCargo').value = getVal('cargo', ag.cargo);
        document.getElementById('reqInputClasse').value = getVal('classe', '');
        document.getElementById('reqInputMatricula').value = getVal('matricula', ag.matricula);
        document.getElementById('reqInputVinculo').value = getVal('vinculo', ag.vinculo);
        document.getElementById('reqInputLotacao').value = getVal('local_trabalho', ag.local_trabalho);
        document.getElementById('reqInputAdmissao').value = getVal('data_admissao', '');
        document.getElementById('reqInputCh').value = getVal('carga_horaria', '');
        
        document.getElementById('reqInputEmail').value = getVal('email', ag.email);
        document.getElementById('reqInputTelCelular').value = getVal('telefone_celular', ag.telefone);
        document.getElementById('reqInputTelResidencial').value = getVal('telefone_residencial', '');
        document.getElementById('reqInputTelSetor').value = getVal('telefone_setor', '');
        
        document.getElementById('reqInputEndereco').value = getVal('endereco', '');
        document.getElementById('reqInputEndNumero').value = getVal('numero_residencial', '');
        document.getElementById('reqInputEndApt').value = getVal('apartamento_endereco', '');
        document.getElementById('reqInputEndBairro').value = getVal('bairro', '');
        document.getElementById('reqInputEndCidade').value = getVal('cidade', '');
        document.getElementById('reqInputEndUf').value = getVal('uf', '');
        document.getElementById('reqInputEndCep').value = getVal('cep', '');
        document.getElementById('reqInputEndComplemento').value = getVal('complemento', '');
        
        document.getElementById('reqInputComplemento').value = getVal('informacoes_complementares', '');

        // Populate checklist checkboxes
        for (let i = 1; i <= 33; i++) {
            const chk = document.getElementById(`reqChkItem_${i}`);
            if (chk) {
                if (reqData.selected_items !== undefined && reqData.selected_items !== null) {
                    chk.checked = reqData.selected_items.includes(i);
                } else {
                    chk.checked = window.SAS.pdf.shouldCheckItem(i, ag);
                }
            }
        }

        const reqBtnSave = document.getElementById('reqBtnSave');
        if (!ag.id) {
            reqBtnSave.classList.add('hidden'); // Oculta botão de salvar se for formulário em branco
        } else {
            reqBtnSave.classList.remove('hidden');
        }

        const getFormData = () => {
            const selectedItems = [];
            for (let i = 1; i <= 33; i++) {
                const chk = document.getElementById(`reqChkItem_${i}`);
                if (chk && chk.checked) {
                    selectedItems.push(i);
                }
            }
            return {
                nome_completo: document.getElementById('reqInputNome').value,
                nome_social: document.getElementById('reqInputNomeSocial').value,
                cpf: document.getElementById('reqInputCpf').value,
                rg: document.getElementById('reqInputRg').value,
                orgao_expedidor: document.getElementById('reqInputOrgaoExp').value,
                uf_expedidor: document.getElementById('reqInputUfExp').value,
                
                cargo: document.getElementById('reqInputCargo').value,
                classe: document.getElementById('reqInputClasse').value,
                matricula: document.getElementById('reqInputMatricula').value,
                vinculo: document.getElementById('reqInputVinculo').value,
                local_trabalho: document.getElementById('reqInputLotacao').value,
                data_admissao: document.getElementById('reqInputAdmissao').value,
                carga_horaria: document.getElementById('reqInputCh').value,
                
                email: document.getElementById('reqInputEmail').value,
                telefone_celular: document.getElementById('reqInputTelCelular').value,
                telefone_residencial: document.getElementById('reqInputTelResidencial').value,
                telefone_setor: document.getElementById('reqInputTelSetor').value,
                
                endereco: document.getElementById('reqInputEndereco').value,
                numero_residencial: document.getElementById('reqInputEndNumero').value,
                apartamento_endereco: document.getElementById('reqInputEndApt').value,
                bairro: document.getElementById('reqInputEndBairro').value,
                cidade: document.getElementById('reqInputEndCidade').value,
                uf: document.getElementById('reqInputEndUf').value,
                cep: document.getElementById('reqInputEndCep').value,
                complemento: document.getElementById('reqInputEndComplemento').value,
                
                informacoes_complementares: document.getElementById('reqInputComplemento').value,
                selected_items: selectedItems
            };
        };

        // Actions handlers
        document.getElementById('reqEditModalClose').onclick = () => {
            modal.classList.add('hidden');
        };
        document.getElementById('reqBtnCancel').onclick = () => {
            modal.classList.add('hidden');
        };

        document.getElementById('reqBtnDirect').onclick = () => {
            const formData = getFormData();
            window.SAS.pdf.generateRequerimentoAPDF(ag, formData);
            modal.classList.add('hidden');
        };

        document.getElementById('reqBtnSave').onclick = async () => {
            const formData = getFormData();
            if (ag.id) {
                try {
                    const oldText = reqBtnSave.innerHTML;
                    reqBtnSave.disabled = true;
                    reqBtnSave.innerHTML = '<span class="animate-spin inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full mr-1"></span> Salvando...';
                    
                    const response = await window.SAS.base44.entities.Agendamento.update(ag.id, {
                        requerimento_a_data: JSON.stringify(formData)
                    });
                    
                    ag.requerimento_a_data = response.requerimento_a_data;
                    window.SAS.utils.notify('success', 'Dados do Requerimento salvos com sucesso!');
                    
                    reqBtnSave.disabled = false;
                    reqBtnSave.innerHTML = oldText;
                    
                    window.SAS.pdf.generateRequerimentoAPDF(ag, formData);
                    modal.classList.add('hidden');
                } catch (e) {
                    console.error("Error saving edits:", e);
                    window.SAS.utils.notify('error', 'Erro ao salvar alterações no banco.');
                    reqBtnSave.disabled = false;
                    reqBtnSave.innerHTML = '<i data-lucide="save" class="w-4 h-4"></i> Salvar no Sistema e Gerar';
                }
            }
        };

        document.getElementById('reqTabBtnServidor').click();
        modal.classList.remove('hidden');
        lucide.createIcons();
    },

    /**
     * Mapeia o serviço solicitado para o número do item no Requerimento A
     */
    shouldCheckItem: (num, ag) => {
        const servico = (ag.tipo_servico || "").toLowerCase();
        const obs = (ag.observacao_problema || "").toLowerCase();
        
        // Mapeamento básico
        if (num === 3 && (servico.includes("diploma") || obs.includes("diploma"))) return true;
        if (num === 5 && (servico.includes("exoneração") || obs.includes("exonerar"))) return true;
        if (num === 6 && (servico.includes("rescisão") || obs.includes("rescisao"))) return true;
        if (num === 9 && (servico.includes("licença") && obs.includes("particular"))) return true;
        if (num === 15 && (servico.includes("permanência") || obs.includes("permanência"))) return true;
        if (num === 21 && (servico.includes("averbação") || obs.includes("averbar"))) return true;
        if (num === 27 && (servico.includes("funeral") || obs.includes("funeral"))) return true;
        if (num === 29 && (servico.includes("ppp") || servico.includes("ltcat"))) return true;
        if (num === 33 && (servico.includes("prêmio") || obs.includes("prêmio"))) return true;
        
        return false;
    },

    /**
     * Página de Esclarecimentos (Instruções)
     */
    generateEsclarecimentos: (doc) => {
        doc.setFont("helvetica", "bold");
        doc.setFontSize(12);
        doc.setFillColor(230, 230, 230);
        doc.rect(15, 15, 180, 8, 'F');
        doc.text("ESCLARECIMENTO AO SERVIDOR", 105, 21, { align: "center" });
        
        doc.setFontSize(8.5);
        doc.setFont("helvetica", "normal");
        let y = 30;
        const marginX = 15;
        const text = [
            "01b- AFASTAMENTO PARA CURSO DE PÓS-GRADUAÇÃO: Pós-doutorado, Doutorado, Mestrado, Especialização – Informar o período e finalidade. Quando com ônus para UPE, anexar formulário específico.",
            "02 - AFASTAMENTO PARA CURSO OU CONGRESSO EM TERRITÓRIO NACIONAL OU EXTERIOR – Informar o período e finalidade. Quando com ônus para UPE, anexar formulário específico.",
            "03 - ANOTAÇÃO DE DIPLOMAS /CERTIFICADO DE CURSO – Anexar cópia com autenticação.",
            "04 - REMOÇÃO OU TRANSFERÊNCIA – Mencionar o local desejado e motivo.",
            "05 - EXONERAÇÃO DE CARGO EFETIVO, CARGO COMISSIONADO / DISPENSA DE FUNÇÃO GRATIFICADA",
            "06 - RESCISÃO DE CONTRATO – Reconhecer firma.",
            "07 - PROMOÇÃO POR TITULAÇÃO – Mencionar o cargo e nível atuais e pretendidos; anexar cópia de diploma ou certificado.",
            "08 - INCENTIVO A TITULAÇÃO – Anexar documento comprobatório.",
            "09 - LICENÇA PARA TRATO INTERESSE PARTICULAR / SEM VENCIMENTO– Mencionar o prazo, se é em prorrogação e motivo.",
            "10 - LICENÇAS MÉDICAS: GESTÃO, TRAT. DE SAÚDE, DE DÇA DE FAMILIARES – Mencionar o período e anexar atestado médico. TRATAMENTO DE SAÚDE – Mencionar prazo e atestado médico, com o período da Junta Médica. POR MOTIVO DE DOENÇA PESSOA DA FAMÍLIA – Mencionar prazo, grau de parentesco e anexar atestado médico.",
            "11 - LICENÇA PARA ACOMPANHAR CÔNJUGE – Anexar atestado do órgão onde o cônjuge é servidor ou militar.",
            "12 - DEDICAÇÃO EXCLUSIVA – DE",
            "13- RETIFICAÇÃO DE NOME – Mencionar o nome atual por extenso e anexar documento comprovando a alteração.",
            "14 - READAPTAÇÃO DE FUNÇÃO – Citar motivo e anexar atestado ou documento se houver.",
            "15 - ABONO PERMANÊNCIA.",
            "16 - SALÁRIO FAMÍLIA – Anexar cópia de certidão de nascimento e termo de responsabilidade se houver.",
            "17 - RISCO DE VIDA – Anexar formulário específico.",
            "18 - REVISÃO DE SITUAÇÃO FUNCIONAL.",
            "19 - CONTAGEM DE TEMPO DE SERVIÇO.",
            "20 - CERTIDÃO PARA FINS ESPECÍFICOS – Citar o tipo de Certidão ou Declaração.",
            "21 - AVERBAÇÃO DE TEMPO DE SERVIÇO.",
            "22 - DESAVERBAÇÃO DE TEMPO DE SERVIÇO.",
            "23 - ALTERAÇÃO DE CARGA HORÁRIA.",
            "24 - ANTECIPAÇÃO DO 13º SALÁRIO",
            "25 - AUXÍLIO CRECHE",
            "26 - AUXÍLIO EDUCAÇÃO",
            "27 - AUXÍLIO FUNERAL",
            "28 - AUXÍLIO PARA COMPRA DE MATERIAL ESCOLAR",
            "29 - PPP/LTCAT",
            "30 - PNE - AUXÍLIO NECESSIDADES ESPECIAIS",
            "31 - ABONO DE FALTA – Anexar o atestado se for o caso.",
            "32 - OUTROS CITAR – mencionar assunto e anexar documentos quando necessário.",
            "33 - LICENÇA PRÊMIO – mencionar se concessão ou autorização (GOZO), decênio e período previsto de início e término.",
            "",
            "INFORMAÇÕES COMPLEMENTARES - Relatar documentos, anexar e informações adicionais necessárias."
        ];

        text.forEach(line => {
            const split = doc.splitTextToSize(line, 175);
            doc.text(split, marginX, y);
            y += (split.length * 4) + 2;
            if (y > 280) { doc.addPage(); y = 20; }
        });
    },

    /**
     * Comprovante Oficial de Atendimento (Declaração)
     */
    generateComprovante: async (ag, atendenteNome) => {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        const marginX = 20;

        // 1. Data e Hora de Download (Canto Superior Esquerdo)
        const now = new Date();
        const dateStr = now.toLocaleDateString('pt-BR');
        const timeStr = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
        doc.setFontSize(8);
        doc.setFont("helvetica", "normal");
        doc.text(`${dateStr}, ${timeStr}`, 15, 10);

        // 2. Logo Centralizada
        try {
            const imgGov = await window.SAS.pdf.getBase64Image('../images/govpe.png');
            doc.addImage(imgGov, 'PNG', 80, 15, 50, 28);
        } catch (e) { console.warn("Logo não carregada no comprovante"); }

        // 3. Título
        doc.setFontSize(14);
        doc.setFont("helvetica", "bold");
        doc.text("DECLARAÇÃO DE ATENDIMENTO", 105, 55, { align: "center" });

        // 4. Texto Formal Mesclado
        doc.setFontSize(11);
        doc.setFont("helvetica", "normal");
        
        const formatTime = (ts) => {
            if (!ts) return '--:--';
            const d = new Date(ts);
            return isNaN(d.getTime()) ? '--:--' : d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        };

        const dataAgendamento = ag.data_agendamento ? ag.data_agendamento.split('-').reverse().join('/') : '___/___/___';
        const nomeServidor = ag.nome_completo || 'NÃO INFORMADO';
        const cpfServidor = ag.cpf || '___.___.___-__';
        const hInicio = formatTime(ag.hora_atendimento || ag.hora_inicio);
        const hFim = formatTime(ag.hora_conclusao || now);

        const text = `Declaro, para os devidos fins, que ${nomeServidor}, CPF Nº ${cpfServidor}, compareceu ao Serviço de Atendimento ao Servidor - SAS - SES/PE, no dia ${dataAgendamento}, possuindo agendamento com início às ${hInicio} e finalização às ${hFim}, para tratar de assuntos de seu interesse.`;
        
        const splitText = doc.splitTextToSize(text, 170);
        doc.text(splitText, marginX, 75);

        // 5. Fechamento
        let currentY = 75 + (splitText.length * 7) + 15;
        doc.text("Atenciosamente,", marginX, currentY);
        
        // 6. Assinatura Dinâmica (Atendente logado ou vinculado ao registro)
        currentY += 35;
        doc.setFont("helvetica", "bold");
        
        // Prioridade: Nome passado por parâmetro > Nome de Assinatura no objeto > Nome de Exibição no objeto > Fallback
        const chefia = atendenteNome || ag.atendente_assinatura || ag.atendente_nome || "Atendente Responsável"; 
        
        doc.text(chefia, 105, currentY, { align: "center" });
        doc.setFont("helvetica", "normal");
        
        doc.save(`Comprovante_${nomeServidor.replace(/\s+/g, '_')}.pdf`);
    },

    // Helper para converter imagem em Base64
    getBase64Image: (url) => {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.setAttribute('crossOrigin', 'anonymous');
            img.onload = () => {
                const canvas = document.createElement("canvas");
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(img, 0, 0);
                resolve(canvas.toDataURL("image/png"));
            };
            img.onerror = (e) => reject(e);
            img.src = url;
        });
    }
};
