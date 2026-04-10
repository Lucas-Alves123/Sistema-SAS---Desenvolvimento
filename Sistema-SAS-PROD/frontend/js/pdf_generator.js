/**
 * SAS - PDF Generator
 * Responsável por gerar o Requerimento A oficial (2 páginas) e o Comprovante de Atendimento.
 */

window.SAS = window.SAS || {};
window.SAS.pdf = {
    
    // Lista de itens do Requerimento A para mapeamento inteligente
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
     * Gera o PDF do Requerimento A Oficial
     */
    generateRequerimentoA: async (ag) => {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        const marginX = 15;
        let y = 15;

        // --- CABEÇALHO ---
        try {
            // Logos (Tenta carregar, se falhar segue sem logo para não travar)
            const imgGov = await window.SAS.pdf.getBase64Image('/frontend/images/govpe.png');
            const imgSas = await window.SAS.pdf.getBase64Image('/frontend/images/sas_logo_new.png');
            doc.addImage(imgGov, 'PNG', 160, 10, 35, 20);
            doc.addImage(imgSas, 'PNG', 15, 10, 50, 20);
        } catch (e) { console.warn("Logos não carregadas no PDF"); }

        doc.setFont("helvetica", "bold");
        doc.setFontSize(14);
        doc.text("SECRETARIA ESTADUAL DE SAÚDE DE PERNAMBUCO", 105, 38, { align: "center" });
        
        y = 50;

        // --- TABELA 1: REQUERIMENTO TÍTULO ---
        doc.setFillColor(220, 220, 220);
        doc.rect(marginX, y, 180, 8, 'F');
        doc.rect(marginX, y, 180, 8, 'S');
        doc.setFontSize(12);
        doc.text("R E Q U E R I M E N T O", 105, y + 6, { align: "center" });
        y += 8;

        // --- GRID DE IDENTIFICAÇÃO ---
        doc.setFontSize(9);
        const rowH = 7;
        
        // Linha Nome
        doc.rect(marginX, y, 180, rowH);
        doc.text(`NOME: ${ag.nome_completo || ''}`, marginX + 2, y + 5);
        y += rowH;

        // Linha Nome Social
        doc.rect(marginX, y, 180, rowH);
        doc.text(`NOME SOCIAL:`, marginX + 2, y + 5);
        y += rowH;

        // Linha Cargo/Nivel/Matricula/Vinculo
        doc.rect(marginX, y, 60, rowH); doc.text(`CARGO/FUNÇÃO: ${ag.cargo || ''}`, marginX + 2, y + 5);
        doc.rect(marginX + 60, y, 50, rowH); doc.text(`CLASSE/NÍVEL/TITULAÇÃO:`, marginX + 62, y + 5);
        doc.rect(marginX + 110, y, 35, rowH); doc.text(`MATRÍCULA: ${ag.matricula || ''}`, marginX + 112, y + 5);
        doc.rect(marginX + 145, y, 35, rowH); doc.text(`VÍNCULO: ${ag.vinculo || ''}`, marginX + 147, y + 5);
        y += rowH;

        // Linha CPF/RG/Orgao/UF
        doc.rect(marginX, y, 60, rowH * 2); doc.text(`CPF: ${ag.cpf || ''}`, marginX + 2, y + 6);
        doc.rect(marginX + 60, y, 50, rowH * 2); doc.text(`RG:`, marginX + 62, y + 6);
        doc.rect(marginX + 110, y, 35, rowH * 2); doc.text(`ÓRGÃO\nEXPEDIDOR:`, marginX + 112, y + 5);
        doc.rect(marginX + 145, y, 35, rowH * 2); doc.text(`UF:`, marginX + 147, y + 6);
        y += (rowH * 2);

        // Linha Lotação / Data / CH
        doc.rect(marginX, y, 110, rowH * 2); doc.text(`ÓRGÃO DE LOTAÇÃO: ${ag.local_trabalho || ''}`, marginX + 2, y + 7);
        doc.rect(marginX + 110, y, 35, rowH * 2); doc.text(`DATA\nADMISSÃO:`, marginX + 112, y + 6);
        doc.rect(marginX + 145, y, 35, rowH * 2); doc.text(`C.H.:`, marginX + 147, y + 7);
        y += (rowH * 2);

        // Linha Email / Numero
        doc.rect(marginX, y, 110, rowH); doc.text(`EMAIL: ${ag.email || ''}`, marginX + 2, y + 5);
        doc.rect(marginX + 110, y, 35, rowH); doc.text(`Nº.:`, marginX + 112, y + 5);
        doc.rect(marginX + 145, y, 35, rowH); doc.text(`APT:`, marginX + 147, y + 5);
        y += rowH;

        // Linha Telefones
        doc.rect(marginX, y, 60, rowH * 2); doc.text(`TELEFONE SETOR/UNIDADE:\n(DDD)`, marginX + 2, y + 5);
        doc.rect(marginX + 60, y, 50, rowH * 2); doc.text(`TELEFONE RESIDENCIAL:\n(DDD)`, marginX + 62, y + 5);
        doc.rect(marginX + 110, y, 70, rowH * 2); doc.text(`TELEFONE CELULAR:\n(DDD)`, marginX + 112, y + 5);
        y += (rowH * 2);

        // Linha Endereço
        doc.rect(marginX, y, 110, rowH); doc.text(`ENDEREÇO:`, marginX + 2, y + 5);
        doc.rect(marginX + 110, y, 35, rowH); doc.text(`Nº`, marginX + 112, y + 5);
        doc.rect(marginX + 145, y, 35, rowH); doc.text(`BAIRRO:`, marginX + 147, y + 5);
        y += rowH;

        // Linha Complemento/Cidade/UF/CEP
        doc.rect(marginX, y, 60, rowH); doc.text(`COMPLEMENTO:`, marginX + 2, y + 5);
        doc.rect(marginX + 60, y, 50, rowH); doc.text(`CIDADE:`, marginX + 62, y + 5);
        doc.rect(marginX + 110, y, 35, rowH); doc.text(`UF:`, marginX + 112, y + 5);
        doc.rect(marginX + 145, y, 35, rowH); doc.text(`CEP:`, marginX + 147, y + 5);
        y += rowH;

        // --- SEÇÃO: REQUER AO ---
        doc.setFillColor(220, 220, 220);
        doc.rect(marginX, y, 180, 8, 'F');
        doc.rect(marginX, y, 180, 8, 'S');
        doc.text("R E Q U E R  A O", 105, y + 6, { align: "center" });
        y += 8;

        // Checklist 01 a 33 (Duas colunas)
        const checkH = 6;
        const colW = 90;
        doc.setFontSize(7.5);
        
        for (let i = 0; i < 18; i++) {
            const itemL = i + 1;
            const itemR = i + 19;
            
            // Desenha Coluna Esquerda
            this.drawCheckItem(doc, marginX, y, itemL, ag);
            
            // Desenha Coluna Direita (Se existir item)
            if (itemR <= 33) {
                this.drawCheckItem(doc, marginX + colW, y, itemR, ag);
            } else if (itemR === 34) {
                 // Bloco Decênio no final da direita
                 doc.rect(marginX + colW, y, 15, checkH * 2);
                 doc.text("DECÊNIO", marginX + colW + 1, y + 7);
                 doc.rect(marginX + colW + 15, y, 75, checkH * 2);
                 doc.text("PERÍODO: ___/___/___ A ___/___/___", marginX + colW + 17, y + 7);
            }
            
            y += (itemR === 34 ? checkH * 2 : checkH);
        }

        // --- INFORMAÇÕES COMPLEMENTARES ---
        doc.setFillColor(220, 220, 220);
        doc.rect(marginX, y, 180, 6, 'F');
        doc.rect(marginX, y, 180, 6, 'S');
        doc.text("INFORMAÇÕES COMPLEMENTARES", 105, y + 4.5, { align: "center" });
        y += 6;
        
        // Linhas de texto complementares
        const obsText = (ag.observacao_problema || '') + "\n" + (ag.observacao_solucao || '');
        const splitObs = doc.splitTextToSize(obsText, 175);
        
        doc.rect(marginX, y, 180, 25);
        doc.text(splitObs, marginX + 2, y + 5);
        y += 28;

        // --- BLOCOS DE ASSINATURA ---
        const boxW = 58;
        const boxH = 30;
        const gap = 3;
        
        // Bloco 1: Requerente
        doc.rect(marginX, y, boxW, boxH);
        doc.text("Em: ___/___/___", marginX + 5, y + 8);
        doc.line(marginX + 5, y + 22, marginX + boxW - 5, y + 22);
        doc.setFontSize(6.5);
        doc.text("ASSINATURA DO REQUERENTE", marginX + boxW/2, y + 26, { align: "center" });

        // Bloco 2: Chefia
        doc.rect(marginX + boxW + gap, y, boxW, boxH);
        doc.text("Em: ___/___/___", marginX + boxW + gap + 5, y + 8);
        doc.line(marginX + boxW + gap + 5, y + 22, marginX + boxW + gap + boxW - 5, y + 22);
        doc.text("ASSINATURA DA CHEFIA IMEDIATA", marginX + boxW + gap + boxW/2, y + 26, { align: "center" });

        // Bloco 3: Diretor
        doc.rect(marginX + (boxW + gap) * 2, y, boxW, boxH);
        doc.text("Em: ___/___/___", marginX + (boxW + gap) * 2 + 5, y + 8);
        doc.line(marginX + (boxW + gap) * 2 + 5, y + 22, marginX + (boxW + gap) * 2 + boxW - 5, y + 22);
        doc.text("ASSINATURA DO GERENTE / DIRETOR", marginX + (boxW + gap) * 2 + boxW/2, y + 26, { align: "center" });

        // --- PÁGINA 2: ESCLARECIMENTOS ---
        doc.addPage();
        this.generateEsclarecimentos(doc);

        doc.save(`Requerimento_A_${ag.nome_completo.replace(/\s+/g, '_')}.pdf`);
    },

    /**
     * Auxiliar para desenhar cada linha do checklist
     */
    drawCheckItem: (doc, x, y, num, ag) => {
        const h = 6;
        const numW = 8;
        const boxW = 8;
        const labelW = 74;

        // Número
        doc.rect(x, y, numW, h);
        doc.setFont("helvetica", "bold");
        doc.text(num.toString().padStart(2, '0'), x + 2, y + 4.5);
        
        // Quadrado (Checkbox)
        doc.rect(x + numW, y, boxW, h);
        
        // Lógica de Marcação (Inteligente)
        if (this.shouldCheckItem(num, ag)) {
            doc.text("X", x + numW + 2.5, y + 4.5);
        }

        // Descrição
        doc.rect(x + numW + boxW, y, labelW, h);
        doc.setFont("helvetica", "normal");
        doc.setFontSize(6.5);
        const text = window.SAS.pdf.requerItems[num - 1];
        doc.text(text, x + numW + boxW + 2, y + 4);
        doc.setFontSize(7.5);
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
     * Comprovante Simples de Atendimento
     */
    generateComprovante: async (ag) => {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        doc.setFontSize(18);
        doc.setFont("helvetica", "bold");
        doc.text("Comprovante de Atendimento - SAS", 105, 30, { align: "center" });

        doc.setFontSize(12);
        doc.setFont("helvetica", "normal");
        const formatTime = (ts) => {
            if (!ts) return '--:--';
            const d = new Date(ts);
            return isNaN(d.getTime()) ? '--:--' : d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        };

        const text = `A servidora/O servidor ${ag.nome_completo} possuía agendamento para o dia ${ag.data_agendamento}, com início às ${formatTime(ag.hora_atendimento)} e finalização às ${formatTime(ag.hora_conclusao)}.`;
        const splitText = doc.splitTextToSize(text, 170);
        doc.text(splitText, 20, 50);

        doc.setFontSize(10);
        doc.text(`Emitido em: ${new Date().toLocaleDateString()} às ${new Date().toLocaleTimeString()}`, 105, 280, { align: "center" });
        
        doc.save(`Comprovante_${ag.nome_completo.replace(/\s+/g, '_')}.pdf`);
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
