// Painel de Chamada - SAS 360
// Desenvolvido para Secretaria de Saúde de Pernambuco

let lastCallId = null;
let lastCallCount = null;
let isFirstRun = true;
let isAudioUnlocked = false;
let announcementInterval = null;
let announcementTimeout = null;
let isAnnouncing = false;

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

        // Check if the call is different from the last one (using ID OR Counter)
        if (data.id && (data.id !== lastCallId || data.chamada_count !== lastCallCount)) {
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
            lastCallCount = data.chamada_count;
        } 
        // Logic to CLEAR the panel if no active call is found or if name is "Aguardando..."
        else if (!data.id || data.nome_completo === "Aguardando...") {
            if (lastCallId !== null) {
                console.log("[PAINEL] Limpando monitor: Voltando para estado Aguardando.");
                updateUI("Aguardando...", "-");
                stopRepeatingAnnouncement();
                lastCallId = null;
                lastCallCount = null;
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
    isAnnouncing = true;
    console.log(`[TTS Cycle] Iniciando ciclo dinâmico para: ${name}`);

    const scheduleNext = () => {
        // Only schedule if we haven't been stopped
        if (!isAnnouncing) {
            console.log("[TTS Cycle] Bloqueado: Atendimento já iniciado.");
            return;
        }

        announcementInterval = setTimeout(() => {
            if (!isAnnouncing) return;
            console.log("[TTS Cycle] Disparando repetição agendada...");
            announceCall(name, guiche, scheduleNext);
        }, 4000); // 4 seconds interval AFTER it finishes speaking
    };

    // First announcement immediate
    announceCall(name, guiche, scheduleNext);
}

function stopRepeatingAnnouncement() {
    isAnnouncing = false;
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
        console.warn("[TTS] Speech Synthesis não suportado neste navegador.");
        return;
    }

    if (!isAudioUnlocked) {
        showAudioOverlay();
        return;
    }

    window.speechSynthesis.cancel();

    const nameLower = (name || "").toLowerCase().trim();
    if (!name || nameLower === "aguardando..." || nameLower.includes("aguardando")) return;

    if (announcementTimeout) clearTimeout(announcementTimeout);
    
    announcementTimeout = setTimeout(() => {
        const cleanGuiche = String(guiche).replace(/\D/g, '') || guiche;
        const phrase = `${name}, dirigir-se ao guichê ${cleanGuiche}.`;
        
        const utterance = new SpeechSynthesisUtterance(phrase);
        utterance.lang = 'pt-BR';
        utterance.rate = 0.82;
        utterance.pitch = 1.0;

        const performSpeech = () => {
            const voices = window.speechSynthesis.getVoices();
            console.log(`[TTS] Total de vozes encontradas: ${voices.length}`);
            
            // Tenta encontrar a voz ideal (Brasil > Portugal > Qualquer PT)
            const ptVoice = voices.find(v => v.name.includes('Google') && v.lang.startsWith('pt')) ||
                           voices.find(v => v.lang.includes('pt-BR') || v.lang.includes('pt_BR')) ||
                           voices.find(v => v.lang.startsWith('pt'));

            if (ptVoice) {
                utterance.voice = ptVoice;
                utterance.lang = ptVoice.lang;
                console.log(`[TTS] EXECUTANDO COM VOZ: ${ptVoice.name} (${ptVoice.lang})`);
            } else {
                console.error("[TTS] CRÍTICO: Nenhuma voz em português foi encontrada no sistema!");
                // Se não achar nada, vamos listar as 3 primeiras vozes apenas para diagnóstico no console
                console.log("[TTS] Vozes disponíveis para diagnóstico:", voices.slice(0, 3).map(v => `${v.name} (${v.lang})`));
            }

            if (onFinishedCallback) {
                utterance.onend = () => onFinishedCallback();
                utterance.onerror = (e) => {
                    console.error("[TTS Error]", e);
                    onFinishedCallback();
                };
            }

            window.speechSynthesis.resume();
            window.speechSynthesis.speak(utterance);
        };

        if (window.speechSynthesis.getVoices().length === 0) {
            window.speechSynthesis.onvoiceschanged = () => {
                window.speechSynthesis.onvoiceschanged = null;
                performSpeech();
            };
        } else {
            performSpeech();
        }
    }, 280); 
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
    setInterval(fetchCurrentCall, 800); // Polling slightly faster (800ms) for better responsiveness

    // Some browsers need this event to load voices properly
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
    }
});
