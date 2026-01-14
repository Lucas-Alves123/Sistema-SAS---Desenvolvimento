
import os

file_path = r'c:\Users\lucas.luna\sistema de atendimento ao servidor - sas\Sistema-SAS---Desenvolvimento\Sistema-SAS---Desenvolvimento\atendimento.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Injection 1: Variables
target_vars = """        const guicheDisplay = document.getElementById('guicheDisplay');
        const alterarGuicheBtn = document.getElementById('alterarGuicheBtn');"""

replacement_vars = """        const guicheDisplay = document.getElementById('guicheDisplay');
        const alterarGuicheBtn = document.getElementById('alterarGuicheBtn');
        const statusToggleBtn = document.getElementById('statusToggleBtn');"""

if target_vars in content:
    content = content.replace(target_vars, replacement_vars)
    print("Successfully injected variables.")
else:
    print("Target variables not found.")

# Injection 2: Logic
target_logic = """        // Guichê Logic
        alterarGuicheBtn.addEventListener('click', () => {
            const newGuiche = prompt('Informe o número do Guichê:', currentGuiche);
            if (newGuiche && newGuiche.trim() !== '') {
                currentGuiche = newGuiche.trim();
                localStorage.setItem('sas_guiche', currentGuiche);
                guicheDisplay.textContent = currentGuiche;
                if (window.toast) window.toast.success(`Guichê alterado para ${currentGuiche}`);
            }
        });"""

replacement_logic = """        // Guichê Logic
        alterarGuicheBtn.addEventListener('click', () => {
            const newGuiche = prompt('Informe o número do Guichê:', currentGuiche);
            if (newGuiche && newGuiche.trim() !== '') {
                currentGuiche = newGuiche.trim();
                localStorage.setItem('sas_guiche', currentGuiche);
                guicheDisplay.textContent = currentGuiche;
                if (window.toast) window.toast.success(`Guichê alterado para ${currentGuiche}`);
            }
        });

        // Status Logic
        let currentStatus = 'disponivel'; // Default

        const updateStatusUI = (status) => {
            currentStatus = status;
            if (status === 'pausa') {
                statusToggleBtn.className = 'bg-red-100 text-red-700 border border-red-200 px-4 py-2 rounded-lg font-bold hover:bg-red-200 transition-all flex items-center gap-2 shadow-sm';
                statusToggleBtn.innerHTML = `
                    <div class="w-3 h-3 rounded-full bg-red-500"></div>
                    <span>Em Pausa</span>
                `;
            } else {
                statusToggleBtn.className = 'bg-green-100 text-green-700 border border-green-200 px-4 py-2 rounded-lg font-bold hover:bg-green-200 transition-all flex items-center gap-2 shadow-sm';
                statusToggleBtn.innerHTML = `
                    <div class="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
                    <span>Online</span>
                `;
            }
        };

        const fetchStatus = async () => {
            try {
                const response = await fetch('/usuarios/online');
                const onlineUsers = await response.json();
                const me = onlineUsers.find(u => u.id === user.id);
                
                if (me && me.status_atendimento) {
                    updateStatusUI(me.status_atendimento);
                }
            } catch (e) {
                console.error('Error fetching status:', e);
            }
        };

        statusToggleBtn.addEventListener('click', async () => {
            const newStatus = currentStatus === 'disponivel' ? 'pausa' : 'disponivel';
            
            // Optimistic UI update
            updateStatusUI(newStatus);

            try {
                const response = await fetch(`/usuarios/${user.id}/status`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });
                
                if (!response.ok) throw new Error('Failed to update status');
                
                if (window.toast) {
                    window.toast.success(newStatus === 'pausa' ? 'Status definido como Pausa' : 'Status definido como Online');
                }
            } catch (e) {
                console.error(e);
                // Revert on error
                updateStatusUI(currentStatus === 'disponivel' ? 'pausa' : 'disponivel');
                if (window.toast) window.toast.error('Erro ao atualizar status');
            }
        });

        // Initialize status
        fetchStatus();"""

if target_logic in content:
    content = content.replace(target_logic, replacement_logic)
    print("Successfully injected logic.")
else:
    print("Target logic not found.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
