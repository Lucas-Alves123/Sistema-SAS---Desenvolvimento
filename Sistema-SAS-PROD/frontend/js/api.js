/**
 * API Client for SAS Application
 * Refactored to connect to Python/Flask Backend
 */

(function () {
    window.SAS = window.SAS || {};

    const API_URL = '/api';

    const fetchWithAuth = async (url, options = {}) => {
        const token = localStorage.getItem('sas_token');
        if (token) {
            options.headers = {
                ...options.headers,
                'Authorization': `Bearer ${token}`
            };
        }
        const res = await fetch(url, options);
        if (res.status === 401 && !url.includes('/login') && !url.includes('/public')) {
            localStorage.removeItem('sas_token');
            localStorage.removeItem('sas_user');
            window.location.href = '/';
        }
        return res;
    };

    // Generic CRUD Helper for Fetch API
    const createCRUD = (endpoint) => ({
        list: async (sort = null) => {
            let url = `${API_URL}/${endpoint}`;
            if (sort) {
                url += `?sort=${sort}`;
            }
            const res = await fetchWithAuth(url);
            if (!res.ok) throw new Error('Failed to fetch data');
            return await res.json();
        },
        get: async (id) => {
            const res = await fetchWithAuth(`${API_URL}/${endpoint}/${id}`);
            if (!res.ok) throw new Error('Failed to fetch item');
            return await res.json();
        },
        filter: async (criteria) => {
            // Server-side filtering
            const params = new URLSearchParams(criteria).toString();
            const res = await fetchWithAuth(`${API_URL}/${endpoint}?${params}`);

            if (!res.ok) throw new Error('Failed to fetch data');
            const data = await res.json();

            if (!Array.isArray(data)) {
                throw new Error('Invalid response from server');
            }

            return data;
        },
        create: async (item) => {
            const res = await fetchWithAuth(`${API_URL}/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(item)
            });
            if (!res.ok) {
                const err = await res.json();
                const errorObj = new Error(err.error || 'Failed to create item');
                errorObj.data = err; // Attach full error data
                throw errorObj;
            }
            return await res.json();
        },
        update: async (id, updates) => {
            const res = await fetchWithAuth(`${API_URL}/${endpoint}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });
            if (!res.ok) {
                const err = await res.json();
                const errorObj = new Error(err.error || 'Failed to update item');
                errorObj.data = err;
                throw errorObj;
            }
            return await res.json();
        },
        delete: async (id) => {
            const res = await fetchWithAuth(`${API_URL}/${endpoint}/${id}`, {
                method: 'DELETE'
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || 'Failed to delete item');
            }
            return true;
        }
    });

    window.SAS.base44 = {
        entities: {
            SystemUser: createCRUD('usuarios'),
            Agendamento: {
                ...createCRUD('agendamentos'),
                getNext: async (channel = null) => {
                    let url = `${API_URL}/agendamentos/proximo`;
                    if (channel) url += `?channel=${encodeURIComponent(channel)}`;
                    const res = await fetchWithAuth(url);
                    if (!res.ok) throw new Error('Failed to fetch next in queue');
                    return await res.json();
                }
            },
            Avaliacao: createCRUD('avaliacoes')
        }
    };

    window.SAS.auth = {
        requestRecovery: async (email) => {
            const res = await fetchWithAuth(`${API_URL}/usuarios/recovery/request`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });
            return await res.json();
        },
        resetPassword: async (token, password) => {
            const res = await fetch(`${API_URL}/usuarios/recovery/reset-with-token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, password })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Erro ao redefinir senha');
            return data;
        }
    };
})();
