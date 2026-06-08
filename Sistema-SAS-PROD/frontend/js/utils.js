/**
 * Utility Functions
 * Refactored for file:// protocol compatibility (no ES modules)
 */

(function () {
    window.SAS = window.SAS || {};
    window.SAS.utils = {};

    window.SAS.utils.createPageUrl = (pageName) => {
        const map = {
            'Home': 'home',
            'Agendamento': 'agendamento',
            'Atendimento': 'atendimento',
            'Monitor': 'monitor',
            'Relatorios': 'relatorios',
            'Usuarios': 'usuarios',
            'Configuracoes': 'configuracoes', // No route for this yet?
            'Login': '/',
            'Identificacao': 'identificacao',
            'Painel': 'painel'
        };
        return map[pageName] || '#';
    };

    window.SAS.utils.formatDate = (dateString) => {
        if (!dateString) return '';
        // Handle YYYY-MM-DD strings to avoid UTC transformation issues
        if (dateString.length === 10 && dateString.includes('-')) {
            const [year, month, day] = dateString.split('-').map(Number);
            return new Date(year, month - 1, day).toLocaleDateString('pt-BR');
        }
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR');
    };

    window.SAS.utils.formatDateTime = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR');
    };

    window.SAS.utils.formatCPF = (value) => {
        let nums = value.replace(/\D/g, '').substring(0, 11);
        if (nums.length <= 3) return nums;
        if (nums.length <= 6) return nums.replace(/(\d{3})(\d+)/, '$1.$2');
        if (nums.length <= 9) return nums.replace(/(\d{3})(\d{3})(\d+)/, '$1.$2.$3');
        return nums.replace(/(\d{3})(\d{3})(\d{3})(\d+)/, '$1.$2.$3-$4');
    };

    window.SAS.utils.formatTelefone = (value) => {
        let nums = value.replace(/\D/g, '').substring(0, 11);
        if (nums.length === 0) return '';
        if (nums.length <= 2) return `(${nums}`;
        if (nums.length <= 6) return `(${nums.substring(0,2)}) ${nums.substring(2)}`;
        if (nums.length <= 10) return `(${nums.substring(0,2)}) ${nums.substring(2,6)}-${nums.substring(6)}`;
        return `(${nums.substring(0,2)}) ${nums.substring(2,7)}-${nums.substring(7)}`;
    };

    window.SAS.utils.cn = (...classes) => {
        return classes.filter(Boolean).join(' ');
    };

    window.SAS.utils.checkAuth = () => {
        const user = localStorage.getItem('sas_user');
        if (!user) {
            window.location.href = '/';
            return null;
        }
        return JSON.parse(user);
    };

    window.SAS.utils.logout = () => {
        localStorage.removeItem('sas_user');
        window.location.href = '/';
    };

    // Global Notification Helper
    window.SAS.utils.notify = (type, message, title) => {
        if (window.toast) {
            if (type === 'success') window.toast.success(message);
            else if (type === 'error') window.toast.error(message);
            else if (type === 'warning') window.toast.warning(message);
            else window.toast(message);
        } else {
            // Fallback to custom modal if toast is not available
            if (window.SAS.utils.modal) {
                const defaultTitle = type === 'error' ? 'Erro' : 'Aviso';
                window.SAS.utils.modal.alert(title || defaultTitle, message, type === 'error' ? 'danger' : 'info');
            } else {
                console.log(`[${type.toUpperCase()}] ${message}`);
                if (type === 'error') alert(message);
            }
        }
    };

    // Global Modal Helper
    window.SAS.utils.modal = {
        confirm: (title, message, callback, type = 'info') => {
            if (window.openGlobalConfirmationModal) {
                window.openGlobalConfirmationModal(title, message, callback, type);
            } else {
                if (confirm(`${title}\n\n${message}`)) callback();
            }
        },
        alert: (title, message, type = 'info') => {
            if (window.openGlobalAlertModal) {
                window.openGlobalAlertModal(title, message, type);
            } else {
                alert(`${title}\n\n${message}`);
            }
        }
    };
})();
