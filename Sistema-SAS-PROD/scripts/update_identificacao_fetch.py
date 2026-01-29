
import re

file_path = r'c:\Users\lucas.luna\sistema de atendimento ao servidor - sas\Sistema-SAS---Desenvolvimento\Sistema-SAS---Desenvolvimento\identificacao.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We want to replace the try block inside the submit handler.
# Key anchor: `const apiUrl =`

new_logic = """            try {
                // Determine Base URL
                let baseUrl = '';
                const hostname = window.location.hostname;
                const port = window.location.port;
                
                // If running on file:// or not on port 5000 (e.g. Live Server on 5500), point to backend
                if (window.location.protocol === 'file:' || (hostname === 'localhost' && port !== '5000') || (hostname === '127.0.0.1' && port !== '5000')) {
                    baseUrl = 'http://localhost:5000';
                }
                
                const apiUrl = `${baseUrl}/api/identificacao/validar?valor=${encodeURIComponent(valor)}`;
                console.log(`[Identificacao] Fetching: ${apiUrl}`);

                const response = await fetch(apiUrl);
                console.log(`[Identificacao] Response Status: ${response.status}`);

                if (response.status !== 200 && response.status !== 404 && response.status !== 400) {
                    throw new Error(`Erro de rede: ${response.status}`);
                }

                const data = await response.json();
                console.log('[Identificacao] Data:', data);

                if (data.success) {
                    currentServidor = data.data;
                    nomeServidor.textContent = currentServidor.nome_completo;
                    dadosServidor.textContent = `CPF: ${currentServidor.cpf || '-'} | Matrícula: ${currentServidor.matricula || '-'}`;

                    successState.classList.remove('hidden');
                    btnBuscar.classList.add('hidden');
                    btnContinuar.classList.remove('hidden');
                    btnContinuar.disabled = false;
                } else {
                    throw new Error(data.message || 'Servidor não encontrado');
                }"""

# Regex to find the block. 
# It starts with `try {` and contains `const apiUrl =`.
# We'll match from `try {` up to `} catch (err) {` (exclusive).

pattern = r'try\s*\{[\s\S]*?const apiUrl =[\s\S]*?\} catch \(err\) \{'

# We need to be careful not to match too much.
# The block ends right before `} catch (err) {`.

# Let's try a simpler replacement based on the `const apiUrl` line if the block is hard to match exactly.
# But replacing the whole block is safer for logic integrity.

# Let's find the start index of `try {` before `const apiUrl`
if 'const apiUrl =' in content:
    idx_api = content.find('const apiUrl =')
    idx_try = content.rfind('try {', 0, idx_api)
    idx_catch = content.find('} catch (err) {', idx_api)
    
    if idx_try != -1 and idx_catch != -1:
        # Extract the old block to verify
        old_block = content[idx_try:idx_catch]
        # Replace
        content = content[:idx_try] + new_logic + "\n            " + content[idx_catch:]
        print("Replaced fetch logic.")
    else:
        print("Could not locate try/catch block boundaries.")
else:
    print("Could not find 'const apiUrl =' anchor.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
