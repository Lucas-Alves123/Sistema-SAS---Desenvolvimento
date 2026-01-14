
import os
import re

file_path = r'c:\Users\lucas.luna\sistema de atendimento ao servidor - sas\Sistema-SAS---Desenvolvimento\Sistema-SAS---Desenvolvimento\identificacao.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Inject HTML Container for Slots
# We'll place it after the attendants grid.
# Look for <div id="attendantsGrid" ...> ... </div>
# It's safer to append it after the grid container.

if 'id="timeSlotsContainer"' not in content:
    # Find the closing div of the attendants grid section or insert before the next section
    # Let's look for the "Próximo" button container in Step 3
    target_btn = '<div class="flex justify-between mt-8">'
    
    slots_html = """
                <!-- Time Slots Section (Hidden by default) -->
                <div id="timeSlotsContainer" class="hidden mt-8 animate-fade-in">
                    <h3 class="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
                        <i data-lucide="clock" class="w-5 h-5 text-blue-600"></i>
                        Horários Disponíveis
                    </h3>
                    <div id="slotsGrid" class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
                        <!-- Slots will be injected here -->
                    </div>
                    <p id="slotsMessage" class="text-sm text-slate-500 mt-2 hidden"></p>
                </div>

                """
    
    if target_btn in content:
        content = content.replace(target_btn, slots_html + target_btn)
        print("Injected HTML container.")
    else:
        print("Could not find target for HTML container.")

# 2. Update JS Logic
# We need to replace `selectAttendantAsync` again.
# This time, instead of auto-selecting, it will render the slots.

new_js_logic = """
        async function selectAttendantAsync(attendant) {
            // 1. Highlight selection
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

            // 2. Reset Slots UI
            const slotsContainer = document.getElementById('timeSlotsContainer');
            const slotsGrid = document.getElementById('slotsGrid');
            const slotsMessage = document.getElementById('slotsMessage');
            const nextBtn = document.getElementById('nextStepBtn');
            
            slotsContainer.classList.remove('hidden');
            slotsGrid.innerHTML = '<div class="col-span-full text-center text-slate-500 py-4"><i data-lucide="loader-2" class="w-5 h-5 animate-spin mx-auto mb-2"></i>Verificando disponibilidade...</div>';
            slotsMessage.classList.add('hidden');
            
            // Disable Next Button until slot is selected
            selectedTime = null;
            updateNextButtonState();
            lucide.createIcons();

            // 3. Fetch Availability
            const dateStr = new Date().toISOString().split('T')[0]; // Today
            const data = await fetchAvailability(attendant.id, dateStr);
            
            slotsGrid.innerHTML = ''; // Clear loading

            if (!data.available) {
                slotsGrid.innerHTML = `<div class="col-span-full text-center text-red-500 bg-red-50 p-3 rounded-lg border border-red-100">
                    <i data-lucide="alert-circle" class="w-5 h-5 mx-auto mb-1"></i>
                    ${data.message || 'Atendente indisponível.'}
                </div>`;
                lucide.createIcons();
                return;
            }
            
            if (data.slots.length === 0) {
                slotsGrid.innerHTML = `<div class="col-span-full text-center text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-100">
                    Não há horários livres para hoje.
                </div>`;
                return;
            }

            // 4. Render Slots
            data.slots.forEach(time => {
                const btn = document.createElement('button');
                btn.className = 'slot-btn bg-white border border-slate-200 text-slate-700 py-2 px-3 rounded-lg font-medium hover:border-blue-500 hover:text-blue-600 hover:bg-blue-50 transition-all focus:outline-none focus:ring-2 focus:ring-blue-200';
                btn.textContent = time;
                btn.onclick = () => selectTimeSlot(btn, time);
                slotsGrid.appendChild(btn);
            });
        }

        function selectTimeSlot(btn, time) {
            // Remove active class from all
            document.querySelectorAll('.slot-btn').forEach(b => {
                b.classList.remove('bg-blue-600', 'text-white', 'border-blue-600', 'hover:bg-blue-700');
                b.classList.add('bg-white', 'text-slate-700', 'border-slate-200', 'hover:bg-blue-50');
            });

            // Add active class to clicked
            btn.classList.remove('bg-white', 'text-slate-700', 'border-slate-200', 'hover:bg-blue-50');
            btn.classList.add('bg-blue-600', 'text-white', 'border-blue-600', 'hover:bg-blue-700');

            selectedTime = time;
            updateNextButtonState();
            
            if (window.toast) window.toast.success(`Horário selecionado: ${time}`);
        }
"""

# Replace the previous selectAttendantAsync function
# We can use regex to find the function body we added previously.
# Or just replace the whole function definition.

# Regex to match `async function selectAttendantAsync(attendant) { ... }`
# Note: The previous injection might have been messy.
# Let's try to match the start and end.

pattern = r'(async function selectAttendantAsync\s*\(\s*attendant\s*\)\s*\{)([\s\S]*?)(\}\s*</script>)'

# If we find it, replace it.
# If not, we might need to append `selectTimeSlot` and overwrite `selectAttendantAsync`.

if "async function selectAttendantAsync" in content:
    # We found it. Let's try to replace the body.
    # Actually, let's just replace the whole function block including the closing script tag 
    # to be sure we append the helper function `selectTimeSlot`.
    
    # Find the start of the function
    start_idx = content.find("async function selectAttendantAsync")
    # Find the end of the script block
    end_idx = content.find("</script>", start_idx)
    
    if start_idx != -1 and end_idx != -1:
        # Construct the new content
        # We keep the </script> at the end
        new_block = new_js_logic + "    </script>"
        content = content[:start_idx] + new_block + content[end_idx+9:]
        print("Replaced selectAttendantAsync logic.")
    else:
        print("Could not locate function boundaries.")
else:
    print("Function selectAttendantAsync not found. Something is wrong.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
