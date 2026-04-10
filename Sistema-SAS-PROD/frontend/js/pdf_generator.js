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
        doc.text(`NOME: ${ag.nome_completo || ''}`, marginX + 2, y + 4.5); y += rowH;

        // R2: NOME SOCIAL
        doc.rect(marginX, y, 180, rowH);
        doc.text(`NOME SOCIAL:`, marginX + 2, y + 4.5); y += rowH;

        // R3: CARGO / CLASSE / MATRICULA / VINCULO
        doc.rect(marginX, y, 65, rowH); doc.text(`CARGO/FUNÇÃO: ${ag.cargo || ''}`, marginX + 2, y + 4.5);
        doc.rect(marginX + 65, y, 50, rowH); doc.text(`CLASSE/NÍVEL/TITULAÇÃO:`, marginX + 66, y + 4.5);
        doc.rect(marginX + 115, y, 35, rowH); doc.text(`MATRÍCULA: ${ag.matricula || ''}`, marginX + 116, y + 4.5);
        doc.rect(marginX + 150, y, 30, rowH); doc.text(`VÍNCULO: ${ag.vinculo || ''}`, marginX + 151, y + 4.5);
        y += rowH;

        // R4: CPF / RG / ORGAO / UF
        doc.rect(marginX, y, 65, rowH * 2); doc.text(`CPF: ${ag.cpf || ''}`, marginX + 2, y + 5);
        doc.rect(marginX + 65, y, 50, rowH * 2); doc.text(`RG:`, marginX + 66, y + 5);
        doc.rect(marginX + 115, y, 35, rowH * 2); doc.text(`ÓRGÃO\nEXPEDIDOR:`, marginX + 116, y + 5);
        doc.rect(marginX + 150, y, 30, rowH * 2); doc.text(`UF:`, marginX + 151, y + 5);
        y += (rowH * 2);

        // R5: LOTAÇÃO / ADMISSÃO / CH
        doc.rect(marginX, y, 120, rowH * 2); doc.text(`ÓRGÃO DE LOTAÇÃO: ${ag.local_trabalho || ''}`, marginX + 2, y + 6);
        doc.rect(marginX + 120, y, 35, rowH * 2); doc.text(`DATA\nADMISSÃO:`, marginX + 121, y + 5.5);
        doc.rect(marginX + 155, y, 25, rowH * 2); doc.text(`C.H.:`, marginX + 156, y + 6);
        y += (rowH * 2);

        // R6: EMAIL / NO. / APT
        doc.rect(marginX, y, 120, rowH); doc.text(`EMAIL: ${ag.email || ''}`, marginX + 2, y + 4.5);
        doc.rect(marginX + 120, y, 35, rowH); doc.text(`Nº.:`, marginX + 121, y + 4.5);
        doc.rect(marginX + 155, y, 25, rowH); doc.text(`APT:`, marginX + 156, y + 4.5);
        y += rowH;

        // R7: TEL SETOR / TEL RESID / TEL CEL
        doc.rect(marginX, y, 65, rowH * 2); doc.text(`TELEFONE SETOR/UNIDADE:\n(DDD)`, marginX + 2, y + 5);
        doc.rect(marginX + 65, y, 55, rowH * 2); doc.text(`TELEFONE RESIDENCIAL:\n(DDD)`, marginX + 66, y + 5);
        doc.rect(marginX + 120, y, 60, rowH * 2); doc.text(`TELEFONE CELULAR:\n(DDD)`, marginX + 121, y + 5);
        y += (rowH * 2);

        // R8: ENDEREÇO / NO / BAIRRO
        doc.rect(marginX, y, 120, rowH); doc.text(`ENDEREÇO:`, marginX + 2, y + 4.5);
        doc.rect(marginX + 120, y, 35, rowH); doc.text(`Nº`, marginX + 121, y + 4.5);
        doc.rect(marginX + 155, y, 25, rowH); doc.text(`BAIRRO:`, marginX + 156, y + 4.5);
        y += rowH;

        // R9: COMPLEMENTO / CIDADE / UF / CEP
        doc.rect(marginX, y, 65, rowH); doc.text(`COMPLEMENTO:`, marginX + 2, y + 4.5);
        doc.rect(marginX + 65, y, 55, rowH); doc.text(`CIDADE:`, marginX + 66, y + 4.5);
        doc.rect(marginX + 120, y, 35, rowH); doc.text(`UF:`, marginX + 121, y + 4.5);
        doc.rect(marginX + 155, y, 25, rowH); doc.text(`CEP:`, marginX + 156, y + 4.5);
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
            window.SAS.pdf.drawCheckItem(doc, marginX, y, itemL, ag);
            
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
                window.SAS.pdf.drawCheckItem(doc, marginX + colW, y, itemR, ag);
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
        const obs1 = (ag.observacao_problema || '').trim();
        const obs2 = (ag.observacao_solucao || '').trim();
        let fullObs = obs1 + (obs1 && obs2 ? "\n" : "") + obs2;
        
        // Filtro: Se for apenas uma letra isolada ou lixo de teste (I, II, etc), limpamos
        if (fullObs.length > 5) { 
            const splitObs = doc.splitTextToSize(fullObs, 175);
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

        doc.save(`Requerimento_A_${(ag.nome_completo || 'servidor').replace(/\s+/g, '_')}.pdf`);
    },

    /**
     * Auxiliar para desenhar cada linha do checklist
     */
    drawCheckItem: (doc, x, y, num, ag) => {
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
        
        // Lógica de Marcação (Inteligente)
        if (window.SAS.pdf.shouldCheckItem(num, ag)) {
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
     * Comprovante Oficial de Comparecimento (Declaração)
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
        doc.text("DECLARAÇÃO DE COMPARECIMENTO", 105, 55, { align: "center" });

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
        const hInicio = formatTime(ag.hora_atendimento);
        const hFim = formatTime(ag.hora_conclusao);

        const text = `Declaro, para os devidos fins, que ${nomeServidor}, CPF Nº ${cpfServidor}, compareceu ao Serviço de Atendimento ao Servidor - SAS - SES/PE, no dia ${dataAgendamento}, possuindo agendamento com início às ${hInicio} e finalização às ${hFim}, para tratar de assuntos de seu interesse.`;
        
        const splitText = doc.splitTextToSize(text, 170);
        doc.text(splitText, marginX, 75);

        // 5. Fechamento
        let currentY = 75 + (splitText.length * 7) + 15;
        doc.text("Atenciosamente,", marginX, currentY);
        
        // 6. Assinatura Dinâmica (Atendente logado)
        currentY += 35;
        doc.setFont("helvetica", "bold");
        const chefia = atendenteNome || "Daisy Santana Maciel de Barros"; 
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
