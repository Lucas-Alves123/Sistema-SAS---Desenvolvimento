// Index (login) page logic via API
import { login as apiLogin, showToast } from './auth.js';

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const usernameField = document.getElementById('username');
    const passwordField = document.getElementById('password');
    const rememberEl = document.getElementById('rememberMe');
    const errorMessage = document.getElementById('errorMessage');
    const forgotLink = document.getElementById('forgotPassword');
    const forgotModal = document.getElementById('forgotPasswordModal');
    const modalClose = document.getElementById('modalClose');

    function showError(msg) {
        if (!errorMessage) return alert(msg);
        errorMessage.textContent = msg;
        errorMessage.classList.add('show');
        errorMessage.style.display = 'block';
        if (usernameField) usernameField.classList.add('invalid');
        if (passwordField) passwordField.classList.add('invalid');
    }
    function clearError() {
        if (!errorMessage) return;
        errorMessage.textContent = '';
        errorMessage.classList.remove('show');
        errorMessage.style.display = 'none';
        if (usernameField) usernameField.classList.remove('invalid');
        if (passwordField) passwordField.classList.remove('invalid');
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearError();
            // Zera qualquer sessão anterior para evitar que tokens antigos mantenham login ativo
            try {
                // Limpa apenas os itens necessários
                ['nomeUsuario', 'sga_username', 'sga_login_time', 'token_sas', 'sas_usuario', 'token_expires_at'].forEach(k => 
                    localStorage.removeItem(k)
                );
            } catch (e) {
                console.error('Erro ao limpar localStorage:', e);
            }
            
            const nome = (usernameField.value || '').trim();
            const senha = (passwordField.value || '').trim();
            const remember = !!(rememberEl && rememberEl.checked);
            
            if (!nome || !senha) { 
                showError('Preencha nome/email e senha.'); 
                return; 
            }
            
            try {
                console.log('Tentando fazer login com:', { nome, senha });
                const result = await apiLogin({ nome, senha, remember });
                
                if (result?.usuario?.nome) {
                    const usuario = result.usuario;
                    console.log('Login bem-sucedido, usuário:', usuario);
                    
                    // Salva informações do usuário
                    localStorage.setItem('nomeUsuario', usuario.nome);
                    localStorage.setItem('sga_username', usuario.nome);
                    
                    if (usuario.id !== undefined) {
                        localStorage.setItem('idUsuario', String(usuario.id));
                    }
                    
                    localStorage.setItem('sga_login_time', new Date().toISOString());
                    showToast('Login realizado com sucesso!', 'success');
                    
                    // Pequeno atraso para o usuário ver a mensagem de sucesso
                    setTimeout(() => {
                        window.location.href = 'home.html';
                    }, 500);
                } else {
                    throw new Error('Dados de usuário inválidos na resposta');
                }
            } catch (err) {
                if (err && err.code === 'NOME_INEXISTENTE') {
                    // Redireciona para primeiro acesso com o nome pré-preenchido
                    const q = new URLSearchParams({ nome });
                    window.location.href = `primeiro_acesso.html?${q.toString()}`;
                    return;
                }
                const msg = err?.message || 'Usuário ou senha inválidos';
                showError(msg);
                showToast(msg, 'error');
            }
        });
    }

    // Esqueci a senha -> abre modal com fluxo completo
    (function setupRecoveryModal(){
        const modal = document.getElementById('forgotPasswordModal');
        const openBtn = document.getElementById('forgotPassword');
        const closeBtn = document.getElementById('modalClose');
        const cancelBtn = document.getElementById('cancelRecovery');
        const resetBtn = document.getElementById('resetPasswordBtn');
        const nomeEl = document.getElementById('recoveryNome');
        const senhaEl = document.getElementById('recoverySenha');
        const confEl = document.getElementById('recoveryConfirma');
        const BASE = localStorage.getItem('sga_api_base') || 'http://127.0.0.1:5000';

        if (!modal || !openBtn) return;

        function open(){
            modal.classList.add('show');
            modal.setAttribute('aria-hidden','false');
            document.body.classList.add('modal-open');
            // simples animação fade-in via classe 'show' já usada no projeto
            try { nomeEl && nomeEl.focus(); } catch {}
        }
        function close(){
            modal.classList.remove('show');
            modal.setAttribute('aria-hidden','true');
            document.body.classList.remove('modal-open');
        }
        function clearFields(){
            if (nomeEl) nomeEl.value = '';
            if (senhaEl) senhaEl.value = '';
            if (confEl) confEl.value = '';
        }

        openBtn.addEventListener('click', (e) => { e.preventDefault(); open(); });
        if (closeBtn) closeBtn.addEventListener('click', () => close());
        if (cancelBtn) cancelBtn.addEventListener('click', () => { clearFields(); close(); });
        // fechar clicando fora
        modal.addEventListener('click', (e) => { if (e.target === modal) close(); });

        if (resetBtn) {
            resetBtn.addEventListener('click', async () => {
                const nome = (nomeEl?.value || '').trim();
                const senha = (senhaEl?.value || '').trim();
                const conf = (confEl?.value || '').trim();
                if (!nome) { showToast('Informe o nome de usuário.', 'error'); return; }
                if (!senha || !conf) { showToast('Informe e confirme a nova senha.', 'error'); return; }
                if (senha !== conf) { showToast('As senhas não coincidem.', 'error'); return; }
                try {
                    const res = await fetch(`${BASE}/recuperar_senha`, {
                        method: 'POST', headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ nome, senha })
                    });
                    const data = await res.json().catch(() => ({}));
                    if (!res.ok || data?.sucesso === false){
                        const msg = data?.mensagem || 'Falha ao redefinir senha';
                        showToast(msg, 'error');
                        return;
                    }
                    showToast('Senha alterada com sucesso!', 'success');
                    clearFields();
                    close();
                } catch (_) {
                    showToast('Erro de conexão. Tente novamente.', 'error');
                }
            });
        }
    })();

    if (usernameField) usernameField.addEventListener('input', clearError);
    if (passwordField) passwordField.addEventListener('input', clearError);
});

