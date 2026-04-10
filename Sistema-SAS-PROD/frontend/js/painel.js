// Painel de Chamada - SAS 360
// Desenvolvido para Secretaria de Saúde de Pernambuco

let lastCallId = null;
let isFirstRun = true;
let isAudioUnlocked = false;
let announcementInterval = null;
let announcementTimeout = null;

// Update Clock
function updateClock() {
    const now = new Date();
    const dateStr = now.toLocaleDateString('pt-BR');
    const timeStr = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

    document.getElementById('current-date').textContent = dateStr;
    document.getElementById('current-time').textContent = timeStr;
}

// Fetch Current Call
async function fetchCurrentCall() {
    try {
        console.log("[API] Verificando novos chamados...");
        const response = await fetch('/api/agendamentos/chamada-atual');
        const data = await response.json();

        if (data.error) {
            console.error("[API] Erro ao buscar chamada:", data.error);
            return;
        }

        console.log("[API] Dados recebidos:", data);

        // Check if the call is different from the last one (using ID)
        if (data.id && data.id !== lastCallId) {
            console.log(`[PAINEL] Novo chamado detectado: ID ${data.id} - ${data.nome_completo}`);
            updateUI(data.nome_completo, data.guiche);

            // Stop any existing repeat before starting a new one
            stopRepeatingAnnouncement();

            // Voice logic:
            // Relaxed to allow first run announcement if name is valid
            if (data.id && data.nome_completo !== "Aguardando...") {
                console.log("[TTS] Iniciando ciclo de anúncio repetido...");
                startRepeatingAnnouncement(data.nome_completo, data.guiche);
            }

            lastCallId = data.id;
        } 
        // Logic to CLEAR the panel if no active call is found or if name is "Aguardando..."
        else if (!data.id || data.nome_completo === "Aguardando...") {
            if (lastCallId !== null || data.nome_completo === "Aguardando...") {
                if (nameEl && nameEl.textContent !== "Aguardando...") {
                    console.log("[PAINEL] Limpando painel: Nenhum chamado ativo.");
                    updateUI("Aguardando...", "-");
                    stopRepeatingAnnouncement();
                    lastCallId = null;
                }
            }
        }

        isFirstRun = false;
    } catch (error) {
        console.error("[API] Erro na requisição:", error);
    }
}

// Update UI with Animation
function updateUI(name, guiche) {
    const nameEl = document.getElementById('server-name');
    const guicheEl = document.getElementById('guiche-number');
    const contentEl = document.querySelector('.call-content');

    if (!nameEl || !guicheEl || !contentEl) return;

    // Remove animation class if exists
    contentEl.classList.remove('new-call-animation');

    // Update text
    nameEl.textContent = name;
    guicheEl.textContent = guiche;

    // Trigger animation
    if (name !== "Aguardando...") {
        void contentEl.offsetWidth; // Force reflow
        contentEl.classList.add('new-call-animation');

        // Remove pulse after 5 seconds
        setTimeout(() => {
            contentEl.classList.remove('new-call-animation');
        }, 5000);
    }
}

// Repeating Announcement Logic
function startRepeatingAnnouncement(name, guiche) {
    stopRepeatingAnnouncement(); // Safety check
    console.log(`[TTS Cycle] Iniciando ciclo dinâmico para: ${name}`);

    const scheduleNext = () => {
        // Only schedule if we haven't been stopped
        announcementInterval = setTimeout(() => {
            console.log("[TTS Cycle] Disparando repetição agendada...");
            announceCall(name, guiche, scheduleNext);
        }, 5000); // 5 seconds interval AFTER it finishes speaking
    };

    // First announcement immediate
    announceCall(name, guiche, scheduleNext);
}

function stopRepeatingAnnouncement() {
    if (announcementInterval) {
        // It could be either a setInterval (if old code) or setTimeout (new logic)
        clearInterval(announcementInterval);
        clearTimeout(announcementInterval); 
        announcementInterval = null;
        console.log("[TTS Cycle] Ciclo de anúncio parado.");
    }
    if (announcementTimeout) {
        clearTimeout(announcementTimeout);
        announcementTimeout = null;
    }
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
}

// Announce Call with Text-to-Speech
// Refined to strictly find and use Brazilian Portuguese voices
function announceCall(name, guiche, onFinishedCallback = null) {
    if (!window.speechSynthesis) {
        console.warn("[TTS] Speech Synthesis não suportado.");
        return;
    }

    // Check if browser blocked audio automatically
    if (!isAudioUnlocked) {
        showAudioOverlay();
        return;
    }

    // Cancel any current announcement
    window.speechSynthesis.cancel();

    // Block announcement if it's just the waiting state
    const nameLower = (name || "").toLowerCase().trim();
    if (!name || nameLower === "aguardando..." || nameLower.includes("aguardando")) {
        console.log("[TTS] Silenciando estado de espera confirmado.");
        return;
    }

    if (announcementTimeout) clearTimeout(announcementTimeout);
    announcementTimeout = setTimeout(() => {
        // Prepare the text (cleaning guiche number for phonetic clarity)
        const cleanGuiche = String(guiche).replace(/\D/g, '') || guiche; 
        const phrase = `${name}, dirigir-se ao guichê ${cleanGuiche}.`;
        
        console.log(`[TTS] Anunciando agora: "${phrase}"`);

        const utterance = new SpeechSynthesisUtterance(phrase);
        utterance.lang = 'pt-BR'; // High priority setting
        utterance.rate = 0.85;    // Slightly slower for better understanding
        utterance.pitch = 1.0;

        // SELEÇÃO DE VOZ AGRESSIVA
        let voices = window.speechSynthesis.getVoices();
        
        if (voices.length > 0) {
            // Find the best Portuguese voice available on THIS machine
            const ptVoice = voices.find(v => v.name.includes('Google') && (v.lang.includes('pt-BR') || v.lang.includes('pt_BR'))) ||
                            voices.find(v => (v.lang === 'pt-BR' || v.lang === 'pt_BR')) || 
                            voices.find(v => v.lang.includes('pt-BR')) ||
                            voices.find(v => v.lang.startsWith('pt'));
            
            if (ptVoice) {
                console.log(`[TTS] Voz Aplicada: ${ptVoice.name} (${ptVoice.lang})`);
                utterance.voice = ptVoice;
                utterance.lang = ptVoice.lang;
            } else {
                console.warn("[TTS] Nenhuma voz em português encontrada. Usando padrão do navegador com lang=pt-BR.");
            }
        }

        utterance.onstart = () => console.log("[TTS] Fala iniciada.");
        
        if (onFinishedCallback) {
            utterance.onend = () => {
                console.log("[TTS] Fala concluída com sucesso.");
                onFinishedCallback();
            };
            utterance.onerror = (e) => {
                console.error("[TTS Error] Erro detectado:", e);
                // Try to continue the cycle even on error
                onFinishedCallback();
            };
        } else {
            utterance.onerror = (e) => console.error("[TTS Error] Erro detectado:", e);
        }

        window.speechSynthesis.resume();
        window.speechSynthesis.speak(utterance);
    }, 250); 
}

// Interaction Overlay Logic
function showAudioOverlay() {
    const overlay = document.getElementById('audio-unlock-overlay');
    if (overlay && !isAudioUnlocked) {
        overlay.style.display = 'flex';
    }
}

function unlockAudio() {
    isAudioUnlocked = true;
    const overlay = document.getElementById('audio-unlock-overlay');
    if (overlay) overlay.style.display = 'none';

    // Initial silent kick to unlock TTS
    if (window.speechSynthesis) {
        const kick = new SpeechSynthesisUtterance("");
        window.speechSynthesis.speak(kick);
        console.log("[TTS] Áudio desbloqueado pelo usuário.");
        
        // Immediate announcement of what's on screen
        const nameOnScreen = document.getElementById('server-name').textContent;
        const guicheOnScreen = document.getElementById('guiche-number').textContent;
        if (nameOnScreen && nameOnScreen !== "Aguardando...") {
            startRepeatingAnnouncement(nameOnScreen, guicheOnScreen);
        }
    }
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    updateClock();
    setInterval(updateClock, 1000);

    // Click anywhere to unlock audio
    document.addEventListener('click', unlockAudio, { once: true });

    // Initial check to see if we're already "unlocked" (some environments allow it)
    setTimeout(() => {
        if (!isAudioUnlocked) {
            console.log("[PAINEL] Aguardando interação do usuário para áudio.");
            showAudioOverlay();
        }
    }, 2000);

    fetchCurrentCall();
    setInterval(fetchCurrentCall, 3000);

    // Some browsers need this event to load voices properly
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
    }
});
