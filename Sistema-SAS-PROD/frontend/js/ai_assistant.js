(function () {
    window.SAS = window.SAS || {};
    window.SAS.ai = {};

    const CHAT_TITLE = "SAS Assistente";
    const WELCOME_MSG = "Olá! Eu sou o seu **Manual Digital do SAS**. Posso te ajudar com o passo a passo de como usar o sistema. O que você quer aprender agora?";
    const QUICK_QUESTIONS = [
        "Quais serviços estão disponíveis?",
        "Como funciona o agendamento?",
        "Documentos para Aposentadoria",
        "Como trocar minha senha?"
    ];

    window.SAS.ai.init = () => {
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
