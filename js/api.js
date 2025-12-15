/**
 * Mock API Client for SAS Application
 * Refactored for file:// protocol compatibility (no ES modules)
 */

(function () {
    window.SAS = window.SAS || {};

    const DB_KEYS = {
        USERS: 'sas_db_users',
        AGENDAMENTOS: 'sas_db_agendamentos',
        HISTORICO: 'sas_db_historico'
    };

    // Initial Data Seeding
    const seedData = () => {
        if (!localStorage.getItem(DB_KEYS.USERS)) {
            const initialUsers = [
                {
                    id: '1',
                    nome_completo: 'Administrador Sistema',
                    usuario: 'admin',
                    senha: 'admin',
                    email: 'admin@sas.pe.gov.br',
                    tipo: 'adm',
                    situacao: 'ativo',
                    guiche_atual: 1,
                    status_atendimento: 'presencial'
                },
                {
                    id: '2',
                    nome_completo: 'Atendente Padrão',
                    usuario: 'atendente',
                    senha: '123',
                    email: 'atendente@sas.pe.gov.br',
                    tipo: 'usuario',
                    situacao: 'ativo',
                    guiche_atual: 2,
                    status_atendimento: 'presencial'
                }
            ];
            localStorage.setItem(DB_KEYS.USERS, JSON.stringify(initialUsers));
        }

        if (!localStorage.getItem(DB_KEYS.AGENDAMENTOS)) {
            localStorage.setItem(DB_KEYS.AGENDAMENTOS, JSON.stringify([]));
        }

        if (!localStorage.getItem(DB_KEYS.HISTORICO)) {
            localStorage.setItem(DB_KEYS.HISTORICO, JSON.stringify([]));
        }
    };

    seedData();

    // Generic CRUD Helper
    const createCRUD = (key) => ({
        list: async (sort = null) => {
            const data = JSON.parse(localStorage.getItem(key) || '[]');
            if (sort === '-created_date') {
                return data.sort((a, b) => new Date(b.created_date || 0) - new Date(a.created_date || 0));
            }
            return data;
        },
        filter: async (criteria) => {
            const data = JSON.parse(localStorage.getItem(key) || '[]');
            return data.filter(item => {
                return Object.keys(criteria).every(k => item[k] == criteria[k]);
            });
        },
        create: async (item) => {
            const data = JSON.parse(localStorage.getItem(key) || '[]');
            const newItem = {
                ...item,
                id: Date.now().toString(),
                created_date: new Date().toISOString()
            };
            data.push(newItem);
            localStorage.setItem(key, JSON.stringify(data));
            return newItem;
        },
        update: async (id, updates) => {
            const data = JSON.parse(localStorage.getItem(key) || '[]');
            const index = data.findIndex(i => i.id === id);
            if (index !== -1) {
                data[index] = { ...data[index], ...updates };
                localStorage.setItem(key, JSON.stringify(data));
                return data[index];
            }
            throw new Error('Item not found');
        },
        delete: async (id) => {
            const data = JSON.parse(localStorage.getItem(key) || '[]');
            const filtered = data.filter(i => i.id !== id);
            localStorage.setItem(key, JSON.stringify(filtered));
            return true;
        }
    });

    window.SAS.base44 = {
        entities: {
            SystemUser: createCRUD(DB_KEYS.USERS),
            Agendamento: createCRUD(DB_KEYS.AGENDAMENTOS),
            HistoricoAtendimento: createCRUD(DB_KEYS.HISTORICO)
        }
    };
})();
