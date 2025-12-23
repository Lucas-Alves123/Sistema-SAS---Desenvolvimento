/**
 * API Client for SAS Application
 * Refactored to connect to Python/Flask Backend
 */

(function () {
    window.SAS = window.SAS || {};

    const API_URL = 'http://localhost:5000';

    // Generic CRUD Helper for Fetch API
    const createCRUD = (endpoint) => ({
        list: async (sort = null) => {
            let url = `${API_URL}/${endpoint}`;
            if (sort) {
                url += `?sort=${sort}`;
            }
            const res = await fetch(url);
            if (!res.ok) throw new Error('Failed to fetch data');
            return await res.json();
        },
        filter: async (criteria) => {
            // Client-side filtering for now, as backend implements simple list
            // In a larger app, this should be server-side
            const res = await fetch(`${API_URL}/${endpoint}`);
            if (!res.ok) throw new Error('Failed to fetch data');
            const data = await res.json();

            return data.filter(item => {
                return Object.keys(criteria).every(k => item[k] == criteria[k]);
            });
        },
        create: async (item) => {
            const res = await fetch(`${API_URL}/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(item)
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || 'Failed to create item');
            }
            return await res.json();
        },
        update: async (id, updates) => {
            const res = await fetch(`${API_URL}/${endpoint}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || 'Failed to update item');
            }
            return await res.json();
        },
        delete: async (id) => {
            const res = await fetch(`${API_URL}/${endpoint}/${id}`, {
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
            Agendamento: createCRUD('agendamentos')
            // HistoricoAtendimento removed as it was unused
        }
    };
})();
