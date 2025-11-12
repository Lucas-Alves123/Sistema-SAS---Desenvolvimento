// Home page logic
// - Load user, welcome animation, simple hover effects

import { initHeaderUserCommon } from './global.js';

document.addEventListener('DOMContentLoaded', function() {
    if (!window.location.pathname.includes('home.html')) return;
    initHeaderUserCommon();
    initHomePage();
    // no charts on home in this version
});

export function initHomePage() {
    const userNameElement = document.getElementById('userName');
    const userRoleElement = document.getElementById('userRole');
    const welcomeTitleElement = document.getElementById('welcomeTitle');

    loadUserData();
    addCardHoverEffects();
    addMenuHoverEffects();

    function loadUserData() {
        const username = localStorage.getItem('sga_username');
        console.debug('[home] loadUserData - stored username:', username);
        if (username) {
            // Preencher nome no cabeçalho (fallback robusto)
            const display = formatDisplayName(username);
            if (userNameElement) userNameElement.textContent = display;
            const avatarEl = document.querySelector('.user-avatar');
            if (avatarEl) avatarEl.textContent = username.charAt(0).toUpperCase();
            welcomeTitleElement.textContent = `Bem-vindo, ${username}`;
            const role = getUserRole(username);
            if (userRoleElement) userRoleElement.textContent = role;
            animateWelcomeMessage();
            // Ensure header dropdown and actions are bound (in case global init missed)
            ensureHeaderBindings();
            // Small retry loop in case something else later overwrote the header text
            retryPopulateHeader(display, username);
        } else {
            window.location.href = 'index.html';
        }
    }

    function retryPopulateHeader(displayName, rawName) {
        let attempts = 0;
        const max = 4;
        const interval = setInterval(() => {
            attempts++;
            const userNameEl = document.getElementById('userName');
            const avatarEl = document.querySelector('.user-avatar');
            console.debug('[home] retryPopulateHeader attempt', attempts, 'userNameEl?', !!userNameEl, 'avatarEl?', !!avatarEl);
            if (userNameEl && (!userNameEl.textContent || userNameEl.textContent.trim() === 'Carregando...')) {
                userNameEl.textContent = displayName;
            }
            if (avatarEl && (!avatarEl.textContent || avatarEl.textContent.trim() === '')) {
                avatarEl.textContent = rawName.charAt(0).toUpperCase();
            }
            if (attempts >= max) clearInterval(interval);
        }, 150);
    }

    function ensureHeaderBindings() {
        try {
            const userInfo = document.getElementById('userInfo');
            const userDropdown = document.getElementById('userDropdown');
            const changeUser = document.getElementById('changeUser');
            const logout = document.getElementById('logout');
            if (userInfo && userDropdown) {
                userInfo.addEventListener('click', function(e) {
                    e.stopPropagation();
                    userDropdown.classList.toggle('show');
                });
                document.addEventListener('click', function(e) {
                    if (!userInfo.contains(e.target) && !userDropdown.contains(e.target)) {
                        userDropdown.classList.remove('show');
                    }
                });
            }
            if (changeUser) {
                changeUser.addEventListener('click', function(e) {
                    e.preventDefault();
                    localStorage.removeItem('sga_username');
                    localStorage.removeItem('sga_login_time');
                    window.location.href = 'index.html';
                });
            }
            if (logout) {
                logout.addEventListener('click', function(e) {
                    e.preventDefault();
                    localStorage.removeItem('sga_username');
                    localStorage.removeItem('sga_login_time');
                    localStorage.removeItem('sga_remember');
                    window.location.href = 'index.html';
                });
            }
        } catch (err) {
            // Não interrompe a página se houver problema
            console.warn('Erro em ensureHeaderBindings', err);
        }
    }

    function formatDisplayName(name) {
        if (!name) return '';
        const first = name.split(/[\.\s_-]/)[0];
        return first.charAt(0).toUpperCase() + first.slice(1);
    }

    function getUserRole(username) {
        const roles = { 'admin': 'Administrador', 'lucas': 'Usuário', 'usuario': 'Usuário', 'teste': 'Usuário' };
        return roles[username.toLowerCase()] || 'Usuário';
    }

    function animateWelcomeMessage() {
        const welcomeTitle = document.querySelector('.welcome-title');
        const welcomeDivider = document.querySelector('.welcome-divider');
        const institutionalText = document.querySelector('.institutional-text');
        const accessButton = document.querySelector('.access-button');
        const infoCards = document.querySelectorAll('.info-card');
        setTimeout(() => { welcomeTitle.style.opacity = '1'; welcomeTitle.style.transform = 'translateY(0)'; }, 200);
        setTimeout(() => { welcomeDivider.style.width = '100px'; }, 400);
        setTimeout(() => { institutionalText.style.opacity = '1'; institutionalText.style.transform = 'translateY(0)'; }, 600);
        setTimeout(() => { accessButton.style.opacity = '1'; accessButton.style.transform = 'translateY(0)'; }, 800);
        infoCards.forEach((card, index) => {
            setTimeout(() => { card.style.opacity = '1'; card.style.transform = 'translateY(0)'; }, 1000 + (index * 200));
        });
        injectInitialAnimationStyles();
    }

    function addCardHoverEffects() {
        const infoCards = document.querySelectorAll('.info-card');
        infoCards.forEach(card => {
            card.addEventListener('mouseenter', function() { this.style.borderTopColor = getRandomColor(); });
            card.addEventListener('mouseleave', function() { this.style.borderTopColor = '#0033A0'; });
        });
    }

    function addMenuHoverEffects() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('mouseenter', function() { this.style.boxShadow = '0 0 20px rgba(0, 51, 160, 0.3)'; });
            link.addEventListener('mouseleave', function() { this.style.boxShadow = 'none'; });
        });
    }

    function getRandomColor() { const colors = ['#0033A0', '#FFD100', '#EF3340', '#009739']; return colors[Math.floor(Math.random() * colors.length)]; }

    function injectInitialAnimationStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .welcome-title { opacity: 0; transform: translateY(20px); transition: all 0.6s ease; }
            .welcome-divider { width: 0; transition: width 0.8s ease; }
            .institutional-text { opacity: 0; transform: translateY(20px); transition: all 0.6s ease; }
            .access-button { opacity: 0; transform: translateY(20px); transition: all 0.6s ease; }
            .info-card { opacity: 0; transform: translateY(20px); transition: all 0.6s ease; }
        `;
        document.head.appendChild(style);
    }
}


