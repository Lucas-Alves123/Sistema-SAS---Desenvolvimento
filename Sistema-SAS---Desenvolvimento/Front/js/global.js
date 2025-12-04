// Global shared behaviors
import { requireAuth, isLogged, getUser, logout as authLogout } from './auth.js';

// Populate header username across pages and enforce auth
export function tryPopulateHeaderUser() {
    // Seta rótulo amigável imediatamente para evitar 'Carregando...'
    const userNameElement = document.getElementById('userName');
    if (userNameElement && (!userNameElement.textContent || /Carregando/i.test(userNameElement.textContent))) {
        userNameElement.textContent = 'Usuário';
    }
    if (!isLogged()) { redirectToLogin(); return; }
    const user = getUser();
    const displayName = user?.nome || localStorage.getItem('sga_username') || '';
    console.debug('[global] tryPopulateHeaderUser - user:', user, 'displayName:', displayName);
    if (userNameElement) {
        userNameElement.textContent = displayName ? formatDisplayName(displayName) : 'Usuário';
    }
    const avatarEl = document.querySelector('.user-avatar');
    if (avatarEl && displayName) {
        avatarEl.textContent = displayName.charAt(0).toUpperCase();
    }
}

// Setup user dropdown and logout/change user actions
export function initHeaderUserCommon() {
    tryPopulateHeaderUser();
    const userInfo = document.getElementById('userInfo');
    const userDropdown = document.getElementById('userDropdown');
    if (userInfo && userDropdown) {
        userInfo.addEventListener('click', function() {
            userDropdown.classList.toggle('show');
        });
        document.addEventListener('click', function(e) {
            if (!userInfo.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.classList.remove('show');
            }
        });
        // Standardize dropdown labels and emojis
        const changeUser = document.getElementById('changeUser');
        const logout = document.getElementById('logout');
        if (changeUser) changeUser.textContent = '🧍 Trocar de Usuário';
        if (logout) logout.textContent = '🚪 Sair';
    }
    const changeUser = document.getElementById('changeUser');
    const logout = document.getElementById('logout');
    if (changeUser) {
            changeUser.addEventListener('click', function(e) {
                e.preventDefault();
                // Clear only the current session identity so the login shows fresh
                localStorage.removeItem('sga_username');
                localStorage.removeItem('sga_login_time');
                // keep sga_remember untouched so user preference persists
                redirectToLogin();
            });
    }
    if (logout) {
        logout.addEventListener('click', async function(e) {
            e.preventDefault();
            try { await authLogout(); } catch {}
            localStorage.removeItem('sga_username');
            localStorage.removeItem('sga_login_time');
            localStorage.removeItem('sga_remember');
            redirectToLogin();
        });
    }
}

    function formatDisplayName(name) {
        if (!name) return '';
        // If the username is like 'lucas.luna' or 'lucas', take first word and capitalize
        const first = name.split(/[\.\s_-]/)[0];
        return first.charAt(0).toUpperCase() + first.slice(1);
    }

// Enable Relatórios dropdown by click
export function initReportsMenuClick() {
    const relItems = document.querySelectorAll('.nav-item.relatorios');
    relItems.forEach(item => {
        const link = item.querySelector('a.nav-link');
        if (!link) return;
        link.addEventListener('click', function(e) {
            e.preventDefault();
            item.classList.toggle('open');
        });
    });
    document.addEventListener('click', function(e) {
        document.querySelectorAll('.nav-item.relatorios.open').forEach(openItem => {
            if (!openItem.contains(e.target)) {
                openItem.classList.remove('open');
            }
        });
    });
}

// Simple redirect helper
export function redirectToLogin() { window.location.href = 'index.html'; }

// Auto-initialize header when the DOM contains header elements.
// This protects against module ordering issues: if a page includes the header markup
// but some other module didn't call initHeaderUserCommon, we'll still populate it.
document.addEventListener('DOMContentLoaded', () => {
    try {
        const userNameEl = document.getElementById('userName');
        const userInfoEl = document.getElementById('userInfo');
        if (userNameEl || userInfoEl) {
            // call the common initializer which itself calls tryPopulateHeaderUser
            initHeaderUserCommon();
            console.debug('[global] Auto-initialized header on DOMContentLoaded');
        }
    } catch (err) {
        console.warn('[global] error during auto header init', err);
    }
});


