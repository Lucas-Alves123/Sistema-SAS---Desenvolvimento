// usuario.js - controle global de usuário
// - Carrega nome do usuário a partir do localStorage (chave: nomeUsuario)
// - Protege páginas internas contra acesso sem login
// - Controla dropdown do usuário no canto superior direito
// - Ações de Trocar usuário e Sair: limpam o localStorage e redirecionam para index.html

function getStoredUserName() {
  try {
    const userJson = localStorage.getItem('sas_usuario');
    if (userJson) {
      try { const u = JSON.parse(userJson); if (u && u.nome) return String(u.nome); } catch {}
    }
    return localStorage.getItem('nomeUsuario') || '';
  } catch { return ''; }
}

function hasValidToken() {
  try {
    const token = localStorage.getItem('token_sas');
    const expAt = Number(localStorage.getItem('token_expires_at') || 0);
    if (!token) return false;
    if (expAt && Date.now() > expAt) return false;
    return true;
  } catch { return false; }
}

function redirectToLogin() {
  window.location.href = 'index.html';
}

function isLoginPage() {
  const path = (window.location.pathname || '').toLowerCase();
  return path.endsWith('/index.html') || path.endsWith('index.html') || path === '/' || path.endsWith('/');
}

function populateHeader(name) {
  try {
    const userNameEl = document.getElementById('userName');
    if (userNameEl) userNameEl.textContent = name || 'Usuário';
  } catch (_) {}
}

function setupDropdown() {
  try {
    const userInfo = document.getElementById('userInfo');
    const userDropdown = document.getElementById('userDropdown');
    if (userInfo && userDropdown) {
      if (!userInfo.dataset.dropdownBound) {
        userInfo.dataset.dropdownBound = '1';
        userInfo.addEventListener('click', function (e) {
          e.stopPropagation();
          userDropdown.classList.toggle('show');
        });
      }
      if (!document.body.dataset.dropdownDocBound) {
        document.body.dataset.dropdownDocBound = '1';
        document.addEventListener('click', function (e) {
          if (!userInfo.contains(e.target) && !userDropdown.contains(e.target)) {
            userDropdown.classList.remove('show');
          }
        });
      }
    }
  } catch (_) {}
}

function setupActions() {
  function clearLoginOnly(e) {
    if (e) e.preventDefault();
    try {
      ['nomeUsuario','sga_username','sga_login_time','token_sas','sas_usuario','token_expires_at'].forEach(k => localStorage.removeItem(k));
      // preservar preferências como sga_remember
    } catch {}
    redirectToLogin();
  }
  function clearAllAndExit(e) {
    if (e) e.preventDefault();
    try { localStorage.clear(); } catch {}
    redirectToLogin();
  }
  try {
    const changeUser = document.getElementById('changeUser');
    const logout = document.getElementById('logout');
    if (changeUser && !changeUser.dataset.bound) {
      changeUser.dataset.bound = '1';
      changeUser.addEventListener('click', clearLoginOnly);
    }
    if (logout && !logout.dataset.bound) {
      logout.dataset.bound = '1';
      logout.addEventListener('click', clearAllAndExit);
    }
  } catch (_) {}
}

function protectAndLoad() {
  if (isLoginPage()) return; // Não proteger a página de login
  const nome = getStoredUserName();
  if (!hasValidToken() || !nome) { redirectToLogin(); return; }
  populateHeader(nome);
  setupDropdown();
  setupActions();
}

// Executa sempre que a página terminar de carregar
document.addEventListener('DOMContentLoaded', protectAndLoad);

// Exporta minimos utilitários caso precise em outros módulos
export { protectAndLoad };
