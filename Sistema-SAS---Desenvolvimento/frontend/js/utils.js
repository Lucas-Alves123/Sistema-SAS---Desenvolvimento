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
            'Identificacao': 'identificacao'
        };
        return map[pageName] || '#';
    };

    window.SAS.utils.formatDate = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR');
    };

    window.SAS.utils.formatDateTime = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR');
    };

    window.SAS.utils.formatCPF = (value) => {
        const nums = value.replace(/\D/g, '');
        return nums.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4').substring(0, 14);
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
    window.SAS.utils.notify = (type, message) => {
        if (window.toast) {
            if (type === 'success') window.toast.success(message);
            else if (type === 'error') window.toast.error(message);
            else if (type === 'warning') window.toast.warning(message);
            else window.toast(message);
        } else {
            // Fallback
            console.log(`[${type.toUpperCase()}] ${message}`);
            if (type === 'error') alert(message);
        }
    };
})();
