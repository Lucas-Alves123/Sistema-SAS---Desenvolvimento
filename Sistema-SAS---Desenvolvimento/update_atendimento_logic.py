
import os

file_path = r'c:\Users\lucas.luna\sistema de atendimento ao servidor - sas\Sistema-SAS---Desenvolvimento\Sistema-SAS---Desenvolvimento\atendimento.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Logic to replace
target_logic = """        statusToggleBtn.addEventListener('click', async () => {
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
        });"""

replacement_logic = """        statusToggleBtn.addEventListener('click', async () => {
            const newStatus = currentStatus === 'disponivel' ? 'pausa' : 'disponivel';
            let motivo = null;

            if (newStatus === 'pausa') {
                motivo = prompt('Qual o motivo da pausa? (Ex: Almoço, Banheiro)');
                if (motivo === null) return; // Cancelled
                if (!motivo.trim()) motivo = 'Pausa'; // Default
            }
            
            // Optimistic UI update
            updateStatusUI(newStatus);

            try {
                const response = await fetch(`/usuarios/${user.id}/status`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus, motivo: motivo })
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
        });"""

if target_logic in content:
    content = content.replace(target_logic, replacement_logic)
    print("Successfully updated pause logic.")
else:
    print("Target logic not found.")
    # Debug
    print("Searching for:")
    print(target_logic[:100])

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
