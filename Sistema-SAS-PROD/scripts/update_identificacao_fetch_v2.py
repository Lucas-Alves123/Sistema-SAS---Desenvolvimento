
import re

file_path = r'c:\Users\lucas.luna\sistema de atendimento ao servidor - sas\Sistema-SAS---Desenvolvimento\Sistema-SAS---Desenvolvimento\identificacao.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We will replace the entire submit handler logic again to be 100% sure.
# We look for `formIdentificacao.addEventListener('submit', async (e) => {`
# And replace the content inside.

start_marker = "formIdentificacao.addEventListener('submit', async (e) => {"
end_marker = "});"

# We need to find the matching closing brace for the event listener.
# Since it's hard to parse JS with regex, we'll try to match the block we inserted last time or the original block.

# Let's try to find the `try {` block again, as that's where the logic is.
# We will replace the entire `try...catch...finally` block.

new_logic = """            try {
                // FORCE LOCALHOST 5000
                const baseUrl = 'http://localhost:5000';
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
                }
            } catch (err) {
                console.error(err);
                // ALERT THE USER
                alert('Erro ao buscar servidor: ' + err.message);
                
                errorMessage.textContent = err.message.includes('Network') ? 'Erro de conexão com o servidor.' : err.message;
                errorState.classList.remove('hidden');
                btnBuscar.classList.remove('hidden');
                btnContinuar.classList.add('hidden');
            } finally {
                btnBuscar.disabled = false;
                if (!currentServidor) {
                    btnBuscar.innerHTML = '<span>Buscar Servidor</span><i data-lucide="search" class="w-5 h-5"></i>';
                    lucide.createIcons();
                }
            }"""

# Find the start of `try {` inside the submit handler
# We can search for `// Determine Base URL` which we added last time, OR just `try {` if that failed.

if '// Determine Base URL' in content:
    # We found our previous injection
    start_idx = content.find('try {', content.find('// Determine Base URL') - 20)
else:
    # Fallback to finding the first try inside the event listener
    listener_idx = content.find("formIdentificacao.addEventListener('submit'")
    if listener_idx != -1:
        start_idx = content.find('try {', listener_idx)
    else:
        start_idx = -1

if start_idx != -1:
    # Find the end of the finally block
    # It ends with `}` followed by `});` usually.
    # Let's look for `lucide.createIcons();` inside finally, then the closing brace.
    
    finally_idx = content.find('finally {', start_idx)
    if finally_idx != -1:
        # Find the closing brace of finally
        # We can count braces or just look for the specific code pattern at the end of finally
        end_idx = content.find('}', content.find('lucide.createIcons();', finally_idx)) + 1
        
        if end_idx != 0:
            content = content[:start_idx] + new_logic + content[end_idx:]
            print("Replaced logic with hardcoded URL and Alert.")
        else:
            print("Could not find end of finally block.")
    else:
        print("Could not find finally block.")
else:
    print("Could not find try block.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
