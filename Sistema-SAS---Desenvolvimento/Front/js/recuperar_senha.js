import { showToast } from './auth.js';

(function(){
  document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('recuperarForm');
    const nomeEl = document.getElementById('recNome');
    const novaEl = document.getElementById('recNova');
    const confEl = document.getElementById('recConfirma');
    const erroEl = document.getElementById('recErro');

    function showError(msg){ if (erroEl){ erroEl.textContent = msg; erroEl.style.display = 'block'; } else { alert(msg); } }
    function clearError(){ if (erroEl){ erroEl.textContent=''; erroEl.style.display='none'; } }

    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearError();
        const nome = (nomeEl?.value || '').trim();
        const nova = (novaEl?.value || '').trim();
        const conf = (confEl?.value || '').trim();
        if (!nome || !nova || !conf){ showError('Preencha todos os campos.'); return; }
        if (nova !== conf){ showError('As senhas não coincidem.'); return; }
        const BASE = localStorage.getItem('sga_api_base') || 'http://127.0.0.1:5000';
        try {
          const res = await fetch(`${BASE}/recuperar_senha`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome, nova_senha: nova })
          });
          const data = await res.json().catch(() => ({}));
          if (!res.ok || data?.sucesso === false){
            const msg = data?.mensagem || 'Falha ao redefinir senha';
            showError(msg); showToast(msg, 'error'); return;
          }
          showToast('Senha redefinida com sucesso', 'success');
          setTimeout(() => { window.location.href = 'index.html'; }, 600);
        } catch (err){
          showError('Erro de conexão. Tente novamente.');
          showToast('Erro de conexão. Tente novamente.', 'error');
        }
      });
    }
  });
})();
