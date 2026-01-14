
import os

file_path = r'c:\Users\lucas.luna\sistema de atendimento ao servidor - sas\Sistema-SAS---Desenvolvimento\Sistema-SAS---Desenvolvimento\identificacao.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Injection 1: HTML Widget
target_html = """                <!-- Header -->
                <div class="text-center mb-8 md:mb-10">
                    <h1 class="text-2xl md:text-3xl font-bold text-slate-800 leading-tight">
                        Agendamento
                    </h1>
                    <p class="text-slate-500 mt-2 text-sm md:text-base">Siga os passos para marcar seu atendimento</p>
                </div>"""

replacement_html = """                <!-- Header -->
                <div class="text-center mb-8 md:mb-10 relative">
                    <h1 class="text-2xl md:text-3xl font-bold text-slate-800 leading-tight">
                        Agendamento
                    </h1>
                    <p class="text-slate-500 mt-2 text-sm md:text-base">Siga os passos para marcar seu atendimento</p>
                    
                    <!-- Online Attendants Widget -->
                    <div id="onlineAttendantsWidget" class="mt-4 flex flex-wrap justify-center gap-2 animate-fade-in min-h-[30px]">
                        <!-- Populated by JS -->
                        <span class="text-xs text-slate-400 flex items-center gap-1"><i data-lucide="loader-2" class="w-3 h-3 animate-spin"></i> Carregando...</span>
                    </div>
                </div>"""

if target_html in content:
    content = content.replace(target_html, replacement_html)
    print("Successfully injected HTML widget.")
else:
    print("Target HTML not found.")

# Injection 2: JS Logic
# We'll append it before the closing script tag
target_js_end = """    </script>
</body>"""

replacement_js_end = """
        // --- Online Attendants Logic ---
        const onlineWidget = document.getElementById('onlineAttendantsWidget');
        
        async function updateOnlineAttendants() {
            if (!onlineWidget) return;
            
            try {
                const response = await fetch('/usuarios/online');
                const users = await response.json();
                
                if (!users || users.length === 0) {
                    onlineWidget.innerHTML = '<span class="text-xs text-slate-400">Nenhum atendente online</span>';
                    return;
                }

                onlineWidget.innerHTML = '';
                users.forEach(u => {
                    const isPause = u.status_atendimento === 'pausa';
                    const colorClass = isPause ? 'bg-red-100 text-red-700 border-red-200' : 'bg-green-100 text-green-700 border-green-200';
                    const dotClass = isPause ? 'bg-red-500' : 'bg-green-500 animate-pulse';
                    const statusText = isPause ? 'Pausa' : 'Online';
                    
                    const badge = document.createElement('div');
                    badge.className = `flex items-center gap-1.5 px-2.5 py-1 rounded-full border ${colorClass} text-xs font-bold shadow-sm transition-all`;
                    badge.innerHTML = `
                        <div class="w-2 h-2 rounded-full ${dotClass}"></div>
                        <span>${u.nome_completo.split(' ')[0]}</span>
                    `;
                    badge.title = `${u.nome_completo} (${statusText})`;
                    onlineWidget.appendChild(badge);
                });
            } catch (e) {
                console.error('Error fetching online attendants:', e);
            }
        }

        // Poll every 10 seconds
        updateOnlineAttendants();
        setInterval(updateOnlineAttendants, 10000);

    </script>
</body>"""

if target_js_end in content:
    content = content.replace(target_js_end, replacement_js_end)
    print("Successfully injected JS logic.")
else:
    print("Target JS end not found.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
