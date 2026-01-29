
import os

file_path = r'c:\Users\lucas.luna\sistema de atendimento ao servidor - sas\Sistema-SAS---Desenvolvimento\Sistema-SAS---Desenvolvimento\atendimento.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """                <button id="alterarGuicheBtn" class="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center gap-2 shadow-sm">
                    <i data-lucide="settings" class="w-5 h-5"></i>
                    Alterar
                </button>
            </div>"""

replacement = """                <button id="alterarGuicheBtn" class="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center gap-2 shadow-sm">
                    <i data-lucide="settings" class="w-5 h-5"></i>
                    Alterar
                </button>
                
                <!-- Status Toggle -->
                <button id="statusToggleBtn" class="bg-green-100 text-green-700 border border-green-200 px-4 py-2 rounded-lg font-bold hover:bg-green-200 transition-all flex items-center gap-2 shadow-sm">
                    <div class="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
                    <span>Online</span>
                </button>
            </div>"""

if target in content:
    new_content = content.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully injected HTML.")
else:
    print("Target not found.")
    # Debug: print surrounding lines
    idx = content.find('alterarGuicheBtn')
    if idx != -1:
        print("Found 'alterarGuicheBtn' at index", idx)
        print("Surrounding content:")
        print(content[idx:idx+500])
