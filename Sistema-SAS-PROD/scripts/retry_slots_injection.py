
import os

file_path = r'c:\Users\lucas.luna\sistema de atendimento ao servidor - sas\Sistema-SAS---Desenvolvimento\Sistema-SAS---Desenvolvimento\identificacao.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Inject HTML Container
# Target: <div class="flex justify-between mt-8"> (The button container)
# We want to insert BEFORE this.

target_btn_container = '<div class="flex justify-between mt-8">'

slots_html = """
                <!-- Time Slots Section -->
                <div id="timeSlotsContainer" class="hidden mt-8 animate-fade-in">
                    <h3 class="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
                        <i data-lucide="clock" class="w-5 h-5 text-blue-600"></i>
                        Horários Disponíveis
                    </h3>
                    <div id="slotsGrid" class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
                        <!-- Slots injected via JS -->
                    </div>
                    <p id="slotsMessage" class="text-sm text-slate-500 mt-2 hidden"></p>
                </div>
"""

if target_btn_container in content and 'id="timeSlotsContainer"' not in content:
    content = content.replace(target_btn_container, slots_html + "\n" + target_btn_container)
    print("Injected HTML container.")
elif 'id="timeSlotsContainer"' in content:
    print("HTML container already exists.")
else:
    print("Target for HTML container not found.")

# 2. Update JS Logic
# We need to replace `selectAttendantAsync`.
# Since regex failed, let's try to find the function by name and replace the block.
# I'll search for `async function selectAttendantAsync(attendant) {`
# and assume it ends with `</script>` because I put it at the end of the file in the previous step.

func_start = "async function selectAttendantAsync(attendant) {"
if func_start in content:
    start_idx = content.find(func_start)
    # Find the end of the script tag
    end_idx = content.find("</script>", start_idx)
    
    if end_idx != -1:
        new_js = """async function selectAttendantAsync(attendant) {
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
            
            if (slotsContainer) {
                slotsContainer.classList.remove('hidden');
                slotsGrid.innerHTML = '<div class="col-span-full text-center text-slate-500 py-4"><i data-lucide="loader-2" class="w-5 h-5 animate-spin mx-auto mb-2"></i>Verificando disponibilidade...</div>';
            }
            
            // Disable Next Button
            selectedTime = null;
            updateNextButtonState();

            // 3. Fetch Availability
            const dateStr = new Date().toISOString().split('T')[0]; // Today
            const data = await fetchAvailability(attendant.id, dateStr);
            
            if (slotsGrid) slotsGrid.innerHTML = '';

            if (!data.available) {
                if (slotsGrid) slotsGrid.innerHTML = `<div class="col-span-full text-center text-red-500 bg-red-50 p-3 rounded-lg border border-red-100">${data.message || 'Indisponível'}</div>`;
                return;
            }
            
            if (data.slots.length === 0) {
                if (slotsGrid) slotsGrid.innerHTML = `<div class="col-span-full text-center text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-100">Sem horários livres.</div>`;
                return;
            }

            // 4. Render Slots
            data.slots.forEach(time => {
                const btn = document.createElement('button');
                btn.className = 'slot-btn bg-white border border-slate-200 text-slate-700 py-2 px-3 rounded-lg font-medium hover:border-blue-500 hover:text-blue-600 hover:bg-blue-50 transition-all';
                btn.textContent = time;
                btn.onclick = () => selectTimeSlot(btn, time);
                if (slotsGrid) slotsGrid.appendChild(btn);
            });
        }

        function selectTimeSlot(btn, time) {
            document.querySelectorAll('.slot-btn').forEach(b => {
                b.classList.remove('bg-blue-600', 'text-white', 'border-blue-600');
                b.classList.add('bg-white', 'text-slate-700', 'border-slate-200');
            });
            btn.classList.remove('bg-white', 'text-slate-700', 'border-slate-200');
            btn.classList.add('bg-blue-600', 'text-white', 'border-blue-600');
            
            selectedTime = time;
            updateNextButtonState();
        }"""
        
        content = content[:start_idx] + new_js + "\n    " + content[end_idx:]
        print("Updated JS logic.")
    else:
        print("Could not find end of script tag.")
else:
    print("Function selectAttendantAsync not found.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
