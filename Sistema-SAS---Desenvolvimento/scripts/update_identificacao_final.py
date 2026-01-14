
import re

file_path = r'c:\Users\lucas.luna\sistema de atendimento ao servidor - sas\Sistema-SAS---Desenvolvimento\Sistema-SAS---Desenvolvimento\identificacao.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. HTML Replacement
# Find the timeDisplayContainer and replace it with our slots container.
# It looks like:
# <div id="timeDisplayContainer" class="hidden ...">
#    ...
# </div>

# We'll use a regex to match the div and its content.
# Assuming it's inside Step 3 content.

html_pattern = r'(<div id="timeDisplayContainer"[\s\S]*?</div>)'
slots_html = """
                <!-- Time Slots Section -->
                <div id="timeSlotsContainer" class="hidden mt-6 animate-fade-in">
                    <h3 class="text-lg font-bold text-slate-700 mb-3 flex items-center gap-2">
                        <i data-lucide="clock" class="w-5 h-5 text-blue-600"></i>
                        Selecione um Horário
                    </h3>
                    <div id="slotsGrid" class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
                        <!-- Slots injected via JS -->
                    </div>
                    <p id="slotsMessage" class="text-sm text-slate-500 mt-2 hidden"></p>
                </div>
"""

# Check if we can find it
if 'id="timeDisplayContainer"' in content:
    content = re.sub(html_pattern, slots_html, content, count=1)
    print("Replaced HTML container.")
else:
    print("HTML container not found (might have been replaced already).")

# 2. JS - Remove getRandomTime
if 'function getRandomTime()' in content:
    content = re.sub(r'function getRandomTime\(\) \{[\s\S]*?\}', '', content)
    print("Removed getRandomTime.")

# 3. JS - Update loadAttendants
# Remove `attendantTimes[att.id] = getRandomTime();`
content = content.replace('attendantTimes[att.id] = getRandomTime();', '// Random time removed')

# 4. JS - Update Event Listener
# Replace the existing listener for atendenteSelect
listener_pattern = r'(atendenteSelect\.addEventListener\(\'change\', \(e\) => \{[\s\S]*?\}\);)'

new_listener = """
        let selectedTimeSlot = null;

        atendenteSelect.addEventListener('change', async (e) => {
            const selectedId = e.target.value;
            const slotsContainer = document.getElementById('timeSlotsContainer');
            const slotsGrid = document.getElementById('slotsGrid');
            const btnConfirmar = document.getElementById('btnConfirmar');
            
            // Reset
            selectedTimeSlot = null;
            btnConfirmar.disabled = true;
            
            if (!selectedId) {
                slotsContainer.classList.add('hidden');
                return;
            }

            slotsContainer.classList.remove('hidden');
            slotsGrid.innerHTML = '<div class="col-span-full text-center text-slate-500 py-4"><i data-lucide="loader-2" class="w-5 h-5 animate-spin mx-auto mb-2"></i>Verificando disponibilidade...</div>';
            lucide.createIcons();

            // Fetch Availability
            const dateStr = dataInput.value || new Date().toISOString().split('T')[0];
            const data = await fetchAvailability(selectedId, dateStr);
            
            slotsGrid.innerHTML = '';

            if (!data.available) {
                slotsGrid.innerHTML = `<div class="col-span-full text-center text-red-500 bg-red-50 p-3 rounded-lg border border-red-100">${data.message || 'Indisponível'}</div>`;
                return;
            }
            
            if (data.slots.length === 0) {
                slotsGrid.innerHTML = `<div class="col-span-full text-center text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-100">Sem horários livres.</div>`;
                return;
            }

            // Render Slots
            data.slots.forEach(time => {
                const btn = document.createElement('button');
                btn.type = 'button'; // Prevent form submit
                btn.className = 'slot-btn w-full bg-white border border-slate-200 text-slate-700 py-2 px-1 rounded-lg text-sm font-medium hover:border-blue-500 hover:text-blue-600 hover:bg-blue-50 transition-all';
                btn.textContent = time;
                btn.onclick = () => {
                    // Select logic
                    document.querySelectorAll('.slot-btn').forEach(b => {
                        b.classList.remove('bg-blue-600', 'text-white', 'border-blue-600', 'hover:bg-blue-700');
                        b.classList.add('bg-white', 'text-slate-700', 'border-slate-200', 'hover:bg-blue-50');
                    });
                    btn.classList.remove('bg-white', 'text-slate-700', 'border-slate-200', 'hover:bg-blue-50');
                    btn.classList.add('bg-blue-600', 'text-white', 'border-blue-600', 'hover:bg-blue-700');
                    
                    selectedTimeSlot = time;
                    btnConfirmar.disabled = false;
                };
                slotsGrid.appendChild(btn);
            });
        });
"""

if 'atendenteSelect.addEventListener' in content:
    content = re.sub(listener_pattern, new_listener, content, count=1)
    print("Updated Event Listener.")

# 5. JS - Update Submit Handler
# We need to use `selectedTimeSlot` instead of `attendantTimes`.
# Look for `const selectedTime = attendantTimes[selectedAttendantId] || '00:00';`
content = content.replace("const selectedTime = attendantTimes[selectedAttendantId] || '00:00';", "const selectedTime = selectedTimeSlot;")

# 6. Ensure fetchAvailability is present
if "async function fetchAvailability" not in content:
    # Append it
    content = content.replace('    </script>', """
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
    </script>""")
    print("Appended fetchAvailability.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
