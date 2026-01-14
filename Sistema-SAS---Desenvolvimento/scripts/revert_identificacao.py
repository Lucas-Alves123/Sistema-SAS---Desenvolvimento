
import re

file_path = r'c:\Users\lucas.luna\sistema de atendimento ao servidor - sas\Sistema-SAS---Desenvolvimento\Sistema-SAS---Desenvolvimento\identificacao.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We want to replace the entire event listener for formIdentificacao.
# It starts with `formIdentificacao.addEventListener('submit', async (e) => {`
# and ends with `});` before `btnContinuar.addEventListener`.

# Let's find the start.
start_marker = "formIdentificacao.addEventListener('submit', async (e) => {"
start_idx = content.find(start_marker)

# Let's find the next event listener to know where to stop.
next_listener = "btnContinuar.addEventListener('click', () => {"
end_idx = content.find(next_listener)

if start_idx != -1 and end_idx != -1:
    # We need to back up from end_idx to find the closing `});` of the previous block.
    # The previous block ends with `});` followed by some whitespace/newlines.
    
    # Let's search backwards from end_idx for `});`
    block_end = content.rfind('});', 0, end_idx) + 3
    
    new_code = """formIdentificacao.addEventListener('submit', async (e) => {
            e.preventDefault();
            const valor = inputIdentificacao.value.trim();
            if (!valor) return;

            // UI Reset
            feedbackArea.classList.remove('hidden');
            successState.classList.add('hidden');
            errorState.classList.add('hidden');
            btnBuscar.disabled = true;
            btnBuscar.innerHTML = '<i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i> Buscando...';
            lucide.createIcons();

            try {
                // Determine Base URL - Robust Logic
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
                
                if (!response.ok) {
                    if (response.status === 404) {
                        throw new Error('Servidor não encontrado');
                    }
                    throw new Error(`Erro na busca (${response.status})`);
                }

                const data = await response.json();

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
                errorMessage.textContent = err.message;
                errorState.classList.remove('hidden');
                btnBuscar.classList.remove('hidden');
                btnContinuar.classList.add('hidden');
            } finally {
                btnBuscar.disabled = false;
                if (!currentServidor) {
                    btnBuscar.innerHTML = '<span>Buscar Servidor</span><i data-lucide="search" class="w-5 h-5"></i>';
                    lucide.createIcons();
                }
            }
        });"""
    
    content = content[:start_idx] + new_code + "\n\n        " + content[end_idx:]
    print("Replaced submit handler with clean version.")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

else:
    print("Could not find start or end markers.")
    print(f"Start: {start_idx}, End: {end_idx}")
