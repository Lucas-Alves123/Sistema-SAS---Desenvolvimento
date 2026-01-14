
import os

file_path = r'c:\Users\lucas.luna\sistema de atendimento ao servidor - sas\Sistema-SAS---Desenvolvimento\Sistema-SAS---Desenvolvimento\identificacao.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Logic to replace
target_js = """                users.forEach(u => {
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
                });"""

replacement_js = """                users.forEach(u => {
                    const isPause = u.status_atendimento === 'pausa';
                    const colorClass = isPause ? 'bg-red-100 text-red-700 border-red-200' : 'bg-green-100 text-green-700 border-green-200';
                    const dotClass = isPause ? 'bg-red-500' : 'bg-green-500 animate-pulse';
                    
                    let statusText = isPause ? 'Pausa' : 'Online';
                    if (isPause && u.motivo_pausa) {
                        statusText += `: ${u.motivo_pausa}`;
                    }
                    
                    const badge = document.createElement('div');
                    badge.className = `flex items-center gap-1.5 px-2.5 py-1 rounded-full border ${colorClass} text-xs font-bold shadow-sm transition-all cursor-help`;
                    badge.innerHTML = `
                        <div class="w-2 h-2 rounded-full ${dotClass}"></div>
                        <span>${u.nome_completo.split(' ')[0]}</span>
                    `;
                    badge.title = `${u.nome_completo} (${statusText})`;
                    onlineWidget.appendChild(badge);
                });"""

if target_js in content:
    content = content.replace(target_js, replacement_js)
    print("Successfully updated display logic.")
else:
    print("Target display logic not found.")
    # Debug
    print("Searching for:")
    print(target_js[:100])

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
