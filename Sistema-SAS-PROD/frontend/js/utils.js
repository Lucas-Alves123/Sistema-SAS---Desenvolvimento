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

    window.SAS.utils.logout = async () => {
        const token = localStorage.getItem('sas_token');
        if (token) {
            try {
                await fetch('/api/usuarios/logout', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
            } catch (e) {
                console.error('Logout API failed', e);
            }
        }
        localStorage.removeItem('sas_token');
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

    // Holidays (National and Pernambuco)
    window.SAS.utils.holidays = {
        '01-01': 'Confraternização Universal',
        '03-06': 'Data Magna de Pernambuco',
        '04-21': 'Tiradentes',
        '05-01': 'Dia do Trabalhador',
        '06-24': 'São João',
        '09-07': 'Independência do Brasil',
        '10-12': 'Nossa Senhora Aparecida',
        '11-02': 'Finados',
        '11-15': 'Proclamação da República',
        '11-20': 'Dia Nacional de Zumbi e da Consciência Negra',
        '12-25': 'Natal',
        // Moveable holidays (example for 2026, though typically calculated dynamically, we can just add fixed dates or simple month-day mapping)
        '02-16': 'Carnaval (2026)',
        '02-17': 'Carnaval (2026)',
        '02-18': 'Quarta-feira de Cinzas (2026)',
        '04-03': 'Paixão de Cristo (2026)',
        '06-04': 'Corpus Christi (2026)'
    };

    // Flatpickr Init Helper
    window.SAS.utils.initDatePickers = () => {
        if (typeof flatpickr !== 'undefined') {
            flatpickr('input[type="date"]', {
                locale: 'pt',
                dateFormat: 'Y-m-d',
                altInput: true,
                altFormat: 'd/m/Y',
                allowInput: true,
                parseDate: (datestr, format) => {
                    // Trata digitação apenas com números (ex: 21072026 -> 21/07/2026)
                    const nums = datestr.replace(/\D/g, '');
                    if (nums.length === 8) {
                        const day = parseInt(nums.substring(0, 2), 10);
                        const month = parseInt(nums.substring(2, 4), 10) - 1;
                        const year = parseInt(nums.substring(4, 8), 10);
                        return new Date(year, month, day);
                    }
                    return flatpickr.parseDate(datestr, format);
                },
                onDayCreate: function(dObj, dStr, fp, dayElem) {
                    // Extract MM-DD
                    const date = dayElem.dateObj;
                    const month = String(date.getMonth() + 1).padStart(2, '0');
                    const day = String(date.getDate()).padStart(2, '0');
                    const mmdd = `${month}-${day}`;
                    
                    if (window.SAS.utils.holidays[mmdd]) {
                        dayElem.classList.add('holiday-date');
                        dayElem.title = window.SAS.utils.holidays[mmdd];
                    }
                },
                onReady: function(selectedDates, dateStr, instance) {
                    if (instance.altInput) {
                        instance.altInput.addEventListener('input', function(e) {
                            let v = e.target.value.replace(/\D/g, '');
                            if (v.length > 8) v = v.substring(0, 8);
                            
                            let formatted = v;
                            if (v.length >= 5) {
                                formatted = v.substring(0, 2) + '/' + v.substring(2, 4) + '/' + v.substring(4, 8);
                            } else if (v.length >= 3) {
                                formatted = v.substring(0, 2) + '/' + v.substring(2, 4);
                            }
                            
                            e.target.value = formatted;
                        });
                    }
                }
            });
        }
    };

})();
