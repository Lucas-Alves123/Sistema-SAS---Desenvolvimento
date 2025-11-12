// Index (login) page logic
// - Valida login, mostra/oculta senha e controla o modal de recuperação
/**
 * Index (login) logic - clean, self-contained and using only localStorage.
 * Implements login and "Esqueci minha senha" modal flow per requirements.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const loginForm = document.getElementById('loginForm');
    const usernameField = document.getElementById('username');
    const passwordField = document.getElementById('password');
    const errorMessage = document.getElementById('errorMessage');
    const forgotLink = document.getElementById('forgotPassword');
    const forgotModal = document.getElementById('forgotPasswordModal');
    const modalBodyContainer = document.getElementById('forgotModalContent');
    const modalClose = document.getElementById('modalClose');

    // 1) Seed default users if not present (stored as 'senha_<usuario>')
    const defaultUsers = {
        admin: 'admin',
        lucas: '123',
        usuario: '123',
        teste: '123'
    };
    Object.keys(defaultUsers).forEach(u => {
        const key = 'senha_' + u;
        if (localStorage.getItem(key) === null) {
            localStorage.setItem(key, defaultUsers[u]);
        }
    });

    // Helper: show/clear error message under the login form
    function showError(msg) {
        // Visual error below the form (styled in CSS). Also provide a fallback alert.
        if (!errorMessage) return alert(msg);
        // set text and ensure visible + styling (explicit in case CSS is overridden)
        errorMessage.textContent = msg;
        errorMessage.classList.add('show');
        errorMessage.style.display = 'block';
        errorMessage.style.color = '#EF3340';
        errorMessage.style.background = 'rgba(239, 51, 64, 0.1)';
        errorMessage.style.border = '1px solid rgba(239, 51, 64, 0.2)';
        // mark fields as invalid (red border) and bring into view
        if (usernameField) usernameField.classList.add('invalid');
        if (passwordField) passwordField.classList.add('invalid');
        try { errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (e) { /* ignore */ }
    }
    function clearError() {
        if (!errorMessage) return;
        errorMessage.textContent = '';
        errorMessage.classList.remove('show');
        errorMessage.style.display = 'none';
        usernameField.classList.remove('invalid');
        passwordField.classList.remove('invalid');
    }

    // 3) Login handler: validate against localStorage key 'senha_<usuario>'
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            clearError();
            const username = (usernameField.value || '').trim();
            const password = (passwordField.value || '').trim();
            if (!username || !password) { showError('Preencha usuário e senha.'); return; }
            const key = 'senha_' + username.toLowerCase();
            const stored = localStorage.getItem(key);
            if (stored === null) { showError('Usuário ou senha incorretos. Verifique suas credenciais.'); alert('Usuário ou senha incorretos. Verifique suas credenciais.'); return; }
            if (stored === password) {
                // successful login
                localStorage.setItem('usuario_logado', username);
                window.location.href = 'home.html';
            } else {
                showError('Usuário ou senha incorretos. Verifique suas credenciais.');
                alert('Usuário ou senha incorretos. Verifique suas credenciais.');
            }
        });
    }

    // Utility to open/close modal
    function openModal() {
        if (!forgotModal) return;
        forgotModal.classList.add('show');
    }
    function closeModal() {
        if (!forgotModal) return;
        forgotModal.classList.remove('show');
        // restore original default content (if present)
        if (modalBodyContainer) {
            modalBodyContainer.innerHTML = `
                <p>Digite seu e-mail cadastrado para receber instruções de redefinição de senha:</p>
                <div class="input-group">
                    <label for="recoveryEmail" class="input-label">E-mail cadastrado:</label>
                    <input type="email" id="recoveryEmail" class="input-field" placeholder="exemplo@dominio.com">
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn-secondary" id="cancelRecovery">Cancelar</button>
                    <button type="button" class="btn-primary" id="sendRecovery">Enviar</button>
                </div>`;
        }
    }

    // 2) "Esqueci minha senha" flow: open modal and inject username+new-password form
    function showResetForm() {
        if (!modalBodyContainer) return;
        modalBodyContainer.innerHTML = `
            <p>Informe o login do usuário e a nova senha abaixo:</p>
            <div class="input-group">
                <label for="recoveryUsername" class="input-label">Usuário</label>
                <input type="text" id="recoveryUsername" class="input-field" placeholder="Seu usuário">
            </div>
            <div class="input-group password-container" style="position:relative;">
                <label for="recoveryNewPassword" class="input-label">Nova senha</label>
                <input type="password" id="recoveryNewPassword" class="input-field" placeholder="Nova senha">
                <button type="button" id="recoveryToggle" class="password-toggle" aria-label="Mostrar senha"><i class="bi bi-eye" id="recoveryEye"></i></button>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" id="cancelReset">Cancelar</button>
                <button type="button" class="btn-primary" id="saveReset">Salvar</button>
            </div>`;

        // attach handlers for cancel/save/toggle
        const cancelBtn = document.getElementById('cancelReset');
        const saveBtn = document.getElementById('saveReset');
        const toggleBtn = document.getElementById('recoveryToggle');
        const eye = document.getElementById('recoveryEye');
        const passField = document.getElementById('recoveryNewPassword');

        if (cancelBtn) cancelBtn.addEventListener('click', () => { closeModal(); });
        if (saveBtn) saveBtn.addEventListener('click', handleSaveReset);
        if (toggleBtn && passField && eye) {
            toggleBtn.addEventListener('click', (ev) => {
                ev.preventDefault();
                const isPwd = passField.type === 'password';
                passField.type = isPwd ? 'text' : 'password';
                eye.classList.toggle('bi-eye');
                eye.classList.toggle('bi-eye-slash');
            });
        }

        // focus username
        const u = document.getElementById('recoveryUsername'); if (u) u.focus();
    }

    function handleSaveReset() {
        const userEl = document.getElementById('recoveryUsername');
        const passEl = document.getElementById('recoveryNewPassword');
        if (!userEl || !passEl) return alert('Erro interno: modal não encontrado.');
        const user = (userEl.value || '').trim();
        const newPass = (passEl.value || '').trim();
        if (!user || !newPass) return alert('Por favor, informe usuário e nova senha.');
        const key = 'senha_' + user.toLowerCase();
        const existing = localStorage.getItem(key);
        if (existing === null) {
            return alert('Usuário não encontrado.');
        }
        localStorage.setItem(key, newPass);
        closeModal();
        alert('Senha redefinida com sucesso! Faça login novamente.');
    }

    // Bind forgot link
    if (forgotLink) {
        forgotLink.addEventListener('click', (e) => { e.preventDefault(); showResetForm(); openModal(); });
    }
    // close modal when clicking close button or outside
    if (modalClose) modalClose.addEventListener('click', closeModal);
    if (forgotModal) forgotModal.addEventListener('click', (e) => { if (e.target === forgotModal) closeModal(); });

    // clear error when typing
    if (usernameField) usernameField.addEventListener('input', clearError);
    if (passwordField) passwordField.addEventListener('input', clearError);

});

