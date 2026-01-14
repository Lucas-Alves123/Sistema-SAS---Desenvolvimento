
import re

file_path = r'c:\Users\lucas.luna\sistema de atendimento ao servidor - sas\Sistema-SAS---Desenvolvimento\Sistema-SAS---Desenvolvimento\identificacao.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Inject fetchAvailability function
if "async function fetchAvailability" not in content:
    # Insert before the last </script>
    content = content.replace('    </script>', '''
        async function fetchAvailability(attendantId, dateStr) {
            try {
                const response = await fetch(`/agendamentos/disponibilidade?atendente_id=${attendantId}&data=${dateStr}`);
                const data = await response.json();
                return data;
            } catch (e) {
                console.error("Error fetching availability:", e);
                return { available: false, message: "Erro ao verificar disponibilidade." };
            }
        }
    </script>''')
    print("Injected fetchAvailability.")

# 2. Replace the click handler logic
# We look for the block where the attendant card is clicked.
# It usually sets `selectedAttendant = attendant` and then proceeds to step 3.
# We need to intercept this to check availability.

# Regex to find the click handler in renderAttendants
# Pattern: card.onclick = () => { ... selectAttendant(attendant); ... }
# Or: card.addEventListener('click', ... )

# Let's try to find `function selectAttendant(attendant)`
# And modify it to check availability.

# If `selectAttendant` exists:
# We want to change it to be `async` and call `fetchAvailability`.

# Regex for selectAttendant function
# function selectAttendant(attendant) { ... }
# We will replace the body.

pattern = r'(function selectAttendant\s*\(\s*attendant\s*\)\s*\{)([\s\S]*?)(\})'

def replacement(match):
    header = match.group(1)
    body = match.group(2)
    footer = match.group(3)
    
    # We want to keep the UI update parts (highlighting) but change the logic for next step.
    # Actually, it's safer to replace the specific logic that sets the time.
    
    new_body = '''
            // Highlight selection
            selectedAttendant = attendant;
            document.querySelectorAll('.attendant-card').forEach(c => {
                c.classList.remove('ring-2', 'ring-blue-500', 'bg-blue-50');
                c.classList.add('hover:shadow-md');
            });
            const card = document.getElementById(`attendant-${attendant.id}`);
            if (card) {
                card.classList.add('ring-2', 'ring-blue-500', 'bg-blue-50');
                card.classList.remove('hover:shadow-md');
            }

            // Check Availability
            const dateStr = new Date().toISOString().split('T')[0]; // Today
            
            // Show loading or checking...
            const nextBtn = document.getElementById('nextStepBtn');
            const originalText = nextBtn.innerHTML;
            nextBtn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Verificando...';
            
            fetchAvailability(attendant.id, dateStr).then(data => {
                nextBtn.innerHTML = originalText;
                
                if (!data.available) {
                    if (window.toast) window.toast.error(data.message || 'Atendente indisponível.');
                    // Deselect
                    selectedAttendant = null;
                    if (card) card.classList.remove('ring-2', 'ring-blue-500', 'bg-blue-50');
                    return;
                }
                
                if (data.slots.length === 0) {
                    if (window.toast) window.toast.error('Sem horários disponíveis para hoje.');
                    selectedAttendant = null;
                    if (card) card.classList.remove('ring-2', 'ring-blue-500', 'bg-blue-50');
                    return;
                }

                // Auto-select first slot or show slot selection?
                // User requirement: "Se um horário já estiver ocupado: Ele não pode ser selecionado novamente"
                // "Um atendente só pode atender 1 servidor por horário"
                // For now, let's auto-select the first available slot as per previous flow (implied).
                // Or just store the slots.
                
                selectedTime = data.slots[0]; // Auto-select first
                // Update UI to show selected time if needed, or just proceed.
                
                if (window.toast) window.toast.success(`Horário disponível: ${selectedTime}`);
                
                // Enable Next Button logic if it was disabled
                updateNextButtonState();
            });
    '''
    return "async " + header + new_body + footer

# Apply replacement if pattern matches
if "function selectAttendant" in content:
    # This is risky with regex on large file. 
    # Let's try to just replace the specific function if we can identify it clearly.
    # Or, I can append a new function `selectAttendantAsync` and update the onclick to use it.
    pass

# Alternative: Search for where `selectAttendant` is called.
# It's likely in `renderAttendants`.
# `card.onclick = () => selectAttendant(attendant);`

if "selectAttendant(attendant)" in content:
    content = content.replace("selectAttendant(attendant)", "selectAttendantAsync(attendant)")
    
    # Now append the new function
    content = content.replace('    </script>', '''
        async function selectAttendantAsync(attendant) {
            // Highlight selection
            selectedAttendant = attendant;
            document.querySelectorAll('.attendant-card').forEach(c => {
                c.classList.remove('ring-2', 'ring-blue-500', 'bg-blue-50');
                c.classList.add('hover:shadow-md');
            });
            const card = document.getElementById(`attendant-${attendant.id}`);
            if (card) {
                card.classList.add('ring-2', 'ring-blue-500', 'bg-blue-50');
                card.classList.remove('hover:shadow-md');
            }

            // Check Availability
            const dateStr = new Date().toISOString().split('T')[0]; // Today
            
            // Feedback
            if (window.toast) window.toast.info('Verificando disponibilidade...');
            
            const data = await fetchAvailability(attendant.id, dateStr);
            
            if (!data.available) {
                if (window.toast) window.toast.error(data.message || 'Atendente indisponível.');
                // Deselect
                selectedAttendant = null;
                if (card) card.classList.remove('ring-2', 'ring-blue-500', 'bg-blue-50');
                updateNextButtonState();
                return;
            }
            
            if (data.slots.length === 0) {
                if (window.toast) window.toast.error('Sem horários disponíveis para hoje.');
                selectedAttendant = null;
                if (card) card.classList.remove('ring-2', 'ring-blue-500', 'bg-blue-50');
                updateNextButtonState();
                return;
            }

            selectedTime = data.slots[0];
            console.log("Selected time:", selectedTime);
            updateNextButtonState();
        }
    </script>''')
    print("Replaced selectAttendant with Async version.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
