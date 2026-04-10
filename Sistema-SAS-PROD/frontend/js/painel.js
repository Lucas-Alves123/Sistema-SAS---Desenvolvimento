// Painel de Chamada - SAS 360
// Desenvolvido para Secretaria de Saúde de Pernambuco

let lastCallId = null;
let isFirstRun = true;
let isAudioUnlocked = false;
let announcementInterval = null;

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
            if (!isFirstRun && data.id && data.nome_completo !== "Aguardando...") {
                console.log("[TTS] Iniciando ciclo de anúncio repetido...");
                startRepeatingAnnouncement(data.nome_completo, data.guiche);
            } else if (isFirstRun) {
                console.log("[PAINEL] Ignorando anúncio no carregamento inicial.");
            }

            lastCallId = data.id;
        } else if (!data.id && lastCallId !== null) {
            console.log("[PAINEL] Chamado encerrado. Parando repetição e voltando para aguardando.");
            updateUI("Aguardando...", "-");
            stopRepeatingAnnouncement();
            lastCallId = null;
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

    console.log(`[TTS Cycle] Iniciando ciclo para: ${name}`);

    // First announcement
    announceCall(name, guiche);

    // Repeat every 6 seconds (slightly more to avoid overlapping with 3s polling)
    announcementInterval = setInterval(() => {
        console.log("[TTS Cycle] Disparando repetição agendada...");
        announceCall(name, guiche);
    }, 6000);
}

function stopRepeatingAnnouncement() {
    if (announcementInterval) {
        clearInterval(announcementInterval);
        announcementInterval = null;
        console.log("[TTS Cycle] Ciclo de anúncio parado.");
    }
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
}

// Announce Call with Text-to-Speech
function announceCall(name, guiche) {
    if (!window.speechSynthesis) {
        console.warn("[TTS] Speech Synthesis não suportado neste navegador.");
        return;
    }

    // Check if browser blocked it
    if (!isAudioUnlocked) {
        console.warn("[TTS] Áudio bloqueado pelo navegador. Aguardando interação.");
        showAudioOverlay();
        return;
    }

    // CRITICAL: Cancel current speech and wait a bit before starting new one
    window.speechSynthesis.cancel();

    setTimeout(() => {
        const phrase = `${name}, dirigir-se ao guichê ${guiche}.`;
        console.log(`[TTS] Falando agora: "${phrase}"`);

        const utterance = new SpeechSynthesisUtterance(phrase);
        utterance.lang = 'pt-BR';
        utterance.rate = 0.95;
        utterance.pitch = 1.0;

        // Force a Portuguese voice
        const voices = window.speechSynthesis.getVoices();
        if (voices.length > 0) {
            // Find a PT-BR voice
            const ptVoice = voices.find(v => v.lang.includes('pt-BR') || v.lang.includes('pt_BR')) || 
                            voices.find(v => v.lang.includes('pt'));
            
            if (ptVoice) {
                console.log(`[TTS] Voz selecionada: ${ptVoice.name} (${ptVoice.lang})`);
                utterance.voice = ptVoice;
            } else {
                console.warn("[TTS] Nenhuma voz em português encontrada. Usando padrão do navegador.");
            }
        }

        utterance.onstart = () => console.log("[TTS] Reprodução de áudio iniciada.");
        utterance.onerror = (e) => console.error("[TTS] Erro detectado na síntese:", e);

        // Resume just in case it's in a stuck 'paused' state
        window.speechSynthesis.resume();
        window.speechSynthesis.speak(utterance);
    }, 100); // 100ms technical delay for stability
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
