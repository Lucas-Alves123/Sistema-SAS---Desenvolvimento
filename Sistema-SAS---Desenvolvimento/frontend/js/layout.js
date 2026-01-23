/**
 * Layout Management
 * Refactored for file:// protocol compatibility (no ES modules)
 */

(function () {
    window.SAS = window.SAS || {};
    window.SAS.layout = {};

    const renderMenuItem = (label, href, iconName, activePage) => {
        const isActive = activePage === label;
        // Active: Yellow background, dark text. Inactive: Gray text, hover blue.
        const activeClass = isActive
            ? 'bg-yellow-400 text-blue-900 font-bold shadow-sm'
            : 'text-gray-600 hover:text-blue-700 font-medium hover:bg-slate-50';

        return `
            <a href="${href}" class="relative group flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${activeClass} overflow-hidden">
                <i data-lucide="${iconName.toLowerCase()}" class="w-4 h-4 relative z-10"></i>
                <span class="relative z-10">${label}</span>
                
                <!-- Hover Effect: Pernambuco Line Animated Width -->
                <div class="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-blue-600 via-yellow-400 to-red-500 w-0 group-hover:w-full transition-all duration-500 ease-in-out"></div>
            </a>
        `;
    };

    window.SAS.layout.renderLayout = (activePage) => {
        const user = window.SAS.utils.checkAuth();
        if (!user) return;

        const app = document.getElementById('app');
        const userName = user.nome_completo.split(' ')[0];

        // Create Layout Structure
        const layoutHTML = `
            <div class="min-h-screen flex flex-col bg-slate-50 font-sans">
                <!-- Top Navbar -->
                <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
                    <div class="w-full px-4 sm:px-6 lg:px-8">
                        <div class="flex justify-between items-center h-20">
                            
                            <!-- Logo Section -->
                            <div class="flex items-center gap-3">
                                <div class="bg-blue-800 text-white font-bold px-3 py-1.5 rounded text-lg shadow-sm">SAS</div>
                                <div class="flex flex-col leading-tight">
                                    <span class="text-blue-800 font-bold text-sm">SAS</span>
                                    <span class="text-gray-500 text-xs">Sistema de Atendimento</span>
                                </div>
                            </div>

                            <!-- Navigation Menu (Desktop) -->
                            <nav class="hidden md:flex items-center gap-1">
                                ${renderMenuItem('Início', 'home', 'Home', activePage === 'Home' ? 'Início' : activePage)}
                                ${renderMenuItem('Agendamento', 'agendamento', 'Calendar', activePage)}
                                ${renderMenuItem('Atendimento', 'atendimento', 'Headphones', activePage)}
                                ${renderMenuItem('Monitor', 'monitor', 'Monitor', activePage)}
                                ${renderMenuItem('Relatórios', 'relatorios', 'FileText', activePage)}
                                ${renderMenuItem('Usuários', 'usuarios', 'Users', activePage)}
                            </nav>

                            <!-- User Profile & Dropdown -->
                            <div class="relative">
                                <button id="userMenuBtn" class="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors shadow-md shadow-blue-200">
                                    <i data-lucide="user" class="w-4 h-4"></i>
                                    <span class="font-medium">${userName}</span>
                                    <i data-lucide="chevron-down" class="w-4 h-4 transition-transform duration-200" id="chevronIcon"></i>
                                </button>

                                <!-- Dropdown Menu -->
                                <div id="userDropdown" class="hidden absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-slate-100 py-1 z-50 animate-fade-in">

                                    <button id="switchUserBtn" class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-slate-50 flex items-center gap-2">
                                        <i data-lucide="users" class="w-4 h-4"></i>
                                        Trocar de usuário
                                    </button>
                                    <button id="logoutBtn" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2">
                                        <i data-lucide="log-out" class="w-4 h-4"></i>
                                        Sair
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </header>

                <!-- Main Content -->
                <main class="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <div id="page-content"></div>
                </main>

                <!-- Footer -->
                <footer class="bg-blue-800 text-white py-4 mt-auto">
                    <div class="max-w-7xl mx-auto px-4 text-center text-sm font-medium opacity-90">
                        © 2025 SAS — Sistema de Atendimento ao Servidor | Governo de Pernambuco
                    </div>
                </footer>
            </div>
        `;

        // Inject Layout but keep existing content
        const existingContent = app.innerHTML;
        app.innerHTML = layoutHTML + `
            <!-- Global Modal System -->
            <div id="globalModalContainer" class="fixed inset-0 bg-black/50 hidden flex items-center justify-center z-[9999] p-4">
                <div id="globalModal" class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-fade-in">
                    <div class="p-6">
                        <div class="flex items-start gap-4">
                            <div id="globalModalIconContainer" class="bg-blue-100 p-3 rounded-full shrink-0">
                                <i id="globalModalIcon" data-lucide="alert-circle" class="w-6 h-6 text-blue-600"></i>
                            </div>
                            <div class="flex-1">
                                <h3 id="globalModalTitle" class="text-lg font-bold text-slate-800 mb-2">Confirmar Ação</h3>
                                <div id="globalModalMessage" class="text-slate-600">Tem certeza que deseja prosseguir?</div>
                            </div>
                        </div>
                    </div>
                    <div id="globalModalFooter" class="bg-slate-50 p-4 flex justify-end gap-3">
                        <button id="globalModalCancelBtn" class="bg-white border border-slate-300 text-slate-700 font-bold py-2 px-4 rounded-lg hover:bg-slate-50 transition-colors">
                            Cancelar
                        </button>
                        <button id="globalModalConfirmBtn" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg transition-colors shadow-lg shadow-blue-200">
                            Confirmar
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.getElementById('page-content').innerHTML = existingContent;

        // Global Modal Logic
        const modalContainer = document.getElementById('globalModalContainer');
        const modalTitle = document.getElementById('globalModalTitle');
        const modalMessage = document.getElementById('globalModalMessage');
        const modalConfirmBtn = document.getElementById('globalModalConfirmBtn');
        const modalCancelBtn = document.getElementById('globalModalCancelBtn');
        const modalIcon = document.getElementById('globalModalIcon');
        const modalIconContainer = document.getElementById('globalModalIconContainer');

        let globalOnConfirm = null;

        window.openGlobalConfirmationModal = (title, message, callback, type = 'info') => {
            modalTitle.textContent = title;
            modalMessage.innerHTML = message;
            globalOnConfirm = callback;
            modalCancelBtn.classList.remove('hidden');
            modalConfirmBtn.textContent = 'Confirmar';

            // Style based on type
            if (type === 'danger') {
                modalIconContainer.className = 'bg-red-100 p-3 rounded-full shrink-0';
                modalIcon.className = 'w-6 h-6 text-red-600';
                modalIcon.setAttribute('data-lucide', 'alert-triangle');
                modalConfirmBtn.className = 'bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-6 rounded-lg transition-colors shadow-lg shadow-red-200';
            } else {
                modalIconContainer.className = 'bg-blue-100 p-3 rounded-full shrink-0';
                modalIcon.className = 'w-6 h-6 text-blue-600';
                modalIcon.setAttribute('data-lucide', 'alert-circle');
                modalConfirmBtn.className = 'bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg transition-colors shadow-lg shadow-blue-200';
            }

            if (window.lucide) window.lucide.createIcons();
            modalContainer.classList.remove('hidden');
        };

        window.openGlobalAlertModal = (title, message, type = 'info') => {
            modalTitle.textContent = title;
            modalMessage.innerHTML = message;
            globalOnConfirm = null;
            modalCancelBtn.classList.add('hidden');
            modalConfirmBtn.textContent = 'OK';

            // Style based on type
            if (type === 'danger') {
                modalIconContainer.className = 'bg-red-100 p-3 rounded-full shrink-0';
                modalIcon.className = 'w-6 h-6 text-red-600';
                modalIcon.setAttribute('data-lucide', 'alert-triangle');
                modalConfirmBtn.className = 'bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-6 rounded-lg transition-colors shadow-lg shadow-red-200';
            } else {
                modalIconContainer.className = 'bg-blue-100 p-3 rounded-full shrink-0';
                modalIcon.className = 'w-6 h-6 text-blue-600';
                modalIcon.setAttribute('data-lucide', 'alert-circle');
                modalConfirmBtn.className = 'bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg transition-colors shadow-lg shadow-blue-200';
            }

            if (window.lucide) window.lucide.createIcons();
            modalContainer.classList.remove('hidden');
        };

        const closeGlobalModal = () => {
            modalContainer.classList.add('hidden');
            globalOnConfirm = null;
        };

        modalConfirmBtn.addEventListener('click', () => {
            if (globalOnConfirm) globalOnConfirm();
            closeGlobalModal();
        });

        modalCancelBtn.addEventListener('click', closeGlobalModal);

        // Initialize Icons
        if (window.lucide) window.lucide.createIcons();

        // Dropdown Logic
        const userMenuBtn = document.getElementById('userMenuBtn');
        const userDropdown = document.getElementById('userDropdown');
        const chevronIcon = document.getElementById('chevronIcon');
        const switchUserBtn = document.getElementById('switchUserBtn');
        const logoutBtn = document.getElementById('logoutBtn');

        const toggleDropdown = () => {
            const isHidden = userDropdown.classList.contains('hidden');
            if (isHidden) {
                userDropdown.classList.remove('hidden');
                chevronIcon.classList.add('rotate-180');
            } else {
                userDropdown.classList.add('hidden');
                chevronIcon.classList.remove('rotate-180');
            }
        };

        userMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleDropdown();
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!userMenuBtn.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.classList.add('hidden');
                chevronIcon.classList.remove('rotate-180');
            }
        });

        // Logout Actions
        const handleLogout = () => {
            window.SAS.utils.logout();
        };

        switchUserBtn.addEventListener('click', handleLogout);
        logoutBtn.addEventListener('click', handleLogout);

        // Inactivity Logic
        const INACTIVITY_LIMIT = 15 * 60 * 1000; // 15 minutes
        let inactivityTimer;

        const resetInactivityTimer = () => {
            clearTimeout(inactivityTimer);
            inactivityTimer = setTimeout(checkInactivity, INACTIVITY_LIMIT);
        };

        const checkInactivity = async () => {
            const currentUser = JSON.parse(localStorage.getItem('sas_user'));
            if (!currentUser) return;

            try {
                const response = await fetch('/api/usuarios/online');
                if (response.ok) {
                    const onlineUsers = await response.json();
                    const me = onlineUsers.find(u => u.id === currentUser.id);

                    if (me && me.status_atendimento === 'pausa') {
                        console.log('User is paused, skipping auto-logout');
                        resetInactivityTimer();
                        return;
                    }
                }

                alert('Sessão expirada por inatividade.');
                window.SAS.utils.logout();
            } catch (e) {
                console.error('Error checking inactivity status:', e);
                resetInactivityTimer();
            }
        };

        ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, resetInactivityTimer);
        });

        resetInactivityTimer();

        // Heartbeat Logic (Every 30 seconds)
        setInterval(async () => {
            const currentUser = JSON.parse(localStorage.getItem('sas_user'));
            if (currentUser) {
                try {
                    await fetch('/api/usuarios/heartbeat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user_id: currentUser.id })
                    });
                } catch (e) {
                    console.error('Heartbeat failed:', e);
                }
            }
        }, 30000);
    };
})();
