// Painel de Chamada - SAS 360
// Desenvolvido para Secretaria de Saúde de Pernambuco

let lastCallId = null;
let lastCallName = "";
let lastCallGuiche = "";

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
        const response = await fetch('/api/agendamentos/chamada-atual');
        const data = await response.json();

        if (data.error) {
            console.error("Erro ao buscar chamada:", data.error);
            return;
        }

        // Check if the call is different from the last one (using ID)
        if (data.id !== lastCallId) {
            updateUI(data.nome_completo, data.guiche);

            // Only play sound if it's a real call (not "Aguardando...")
            if (data.nome_completo !== "Aguardando...") {
                playCallSound();
            }

            lastCallId = data.id;
            lastCallName = data.nome_completo;
            lastCallGuiche = data.guiche;
        }
    } catch (error) {
        console.error("Erro na requisição:", error);
    }
}

// Update UI with Animation
function updateUI(name, guiche) {
    const nameEl = document.getElementById('server-name');
    const guicheEl = document.getElementById('guiche-number');
    const contentEl = document.querySelector('.call-content');

    // Remove animation class if exists
    contentEl.classList.remove('new-call-animation');

    // Update text
    nameEl.textContent = name;
    guicheEl.textContent = guiche;

    // Trigger animation
    void contentEl.offsetWidth; // Force reflow
    contentEl.classList.add('new-call-animation');

    // Remove pulse after 5 seconds
    setTimeout(() => {
        contentEl.classList.remove('new-call-animation');
    }, 5000);
}

// Play Notification Sound
function playCallSound() {
    const audio = document.getElementById('call-sound');
    if (audio) {
        audio.currentTime = 0;
        audio.play().catch(e => console.log("Erro ao tocar áudio (interação necessária):", e));
    }
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    updateClock();
    setInterval(updateClock, 1000);

    // Start polling immediately for full automation
    fetchCurrentCall();
    setInterval(fetchCurrentCall, 3000); // Poll every 3 seconds
});
