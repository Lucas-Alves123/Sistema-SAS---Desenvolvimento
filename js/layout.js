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
            <a href="${href}" class="flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${activeClass}">
                <i data-lucide="${iconName.toLowerCase()}" class="w-4 h-4"></i>
                <span>${label}</span>
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
                                ${renderMenuItem('Início', 'home.html', 'Home', activePage === 'Home' ? 'Início' : activePage)}
                                ${renderMenuItem('Agendamento', 'agendamento.html', 'Calendar', activePage)}
                                ${renderMenuItem('Atendimento', 'atendimento.html', 'Headphones', activePage)}
                                ${renderMenuItem('Configurações', 'configuracoes.html', 'Settings', activePage)}
                                ${renderMenuItem('Monitor', 'monitor.html', 'Monitor', activePage)}
                                ${renderMenuItem('Relatórios', 'relatorios.html', 'FileText', activePage)}
                                ${renderMenuItem('Usuários', 'usuarios.html', 'Users', activePage)}
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
        app.innerHTML = layoutHTML;
        document.getElementById('page-content').innerHTML = existingContent;

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
    };
})();
