import { login, showToast } from './auth.js';

(function(){
  document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('primeiroForm');
    const nomeEl = document.getElementById('primeiroNome');
    const senhaEl = document.getElementById('primeiroSenha');
    const confEl = document.getElementById('primeiroConfirma');
    const erroEl = document.getElementById('primeiroErro');

    // Prefill from query string
    try {
      const q = new URLSearchParams(window.location.search);
      const nome = q.get('nome') || '';
      if (nome && nomeEl) nomeEl.value = nome;
    } catch {}

    function showError(msg){ if (erroEl){ erroEl.textContent = msg; erroEl.style.display = 'block'; } else { alert(msg); } }
    function clearError(){ if (erroEl){ erroEl.textContent=''; erroEl.style.display='none'; } }

    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearError();
        const nome = (nomeEl?.value || '').trim();
        const senha = (senhaEl?.value || '').trim();
        const confirma = (confEl?.value || '').trim();
        if (!nome || !senha || !confirma){ showError('Preencha todos os campos.'); return; }
        if (senha !== confirma){ showError('As senhas não coincidem.'); return; }
        const BASE = localStorage.getItem('sga_api_base') || 'http://127.0.0.1:5000';
        try {
          const res = await fetch(`${BASE}/primeiro_acesso`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome, senha })
          });
          const data = await res.json().catch(() => ({}));
          if (!res.ok || data?.sucesso === false){
            const msg = data?.mensagem || 'Falha ao criar usuário';
            showError(msg); showToast(msg, 'error'); return;
          }
          showToast('Conta criada! Entrando...', 'success');
          // Auto login
          try { await login({ nome, senha, remember: false }); } catch {}
          // Salvar nome no localStorage
          try { localStorage.setItem('nomeUsuario', nome); localStorage.setItem('sga_username', nome); } catch {}
          window.location.href = 'home.html';
        } catch (err){
          showError('Erro de conexão. Tente novamente.');
          showToast('Erro de conexão. Tente novamente.', 'error');
        }
      });
    }
  });
})();
