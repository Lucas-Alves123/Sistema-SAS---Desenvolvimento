import { getToken, showToast } from './auth.js';

export const API_BASE = localStorage.getItem('sga_api_base') || 'http://localhost:3000';

function buildQuery(params = {}) {
  const q = new URLSearchParams();
  Object.entries(params || {}).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') q.append(k, v);
  });
  const s = q.toString();
  return s ? `?${s}` : '';
}

async function request(path, { method = 'GET', body, headers = {} } = {}) {
  const token = getToken();
  const reqHeaders = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...headers,
  };
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method,
      headers: reqHeaders,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (e) {
    const err = new Error('Falha de conexão com a API');
    err.code = 'NETWORK_ERROR';
    throw err;
  }
  const ct = res.headers.get('content-type') || '';
  const data = ct.includes('application/json') ? await res.json().catch(() => ({})) : await res.text();
  if (res.status === 401) {
    // Token inválido/expirado
    try { localStorage.removeItem('token_sas'); } catch {}
    showToast('Sessão expirada. Faça login novamente.', 'error');
    setTimeout(() => { window.location.href = 'index.html'; }, 500);
    throw new Error('Não autorizado. Faça login novamente.');
  }
  if (!res.ok) {
    const msg = typeof data === 'object' && data && (data.mensagem || data.message || data.error) || res.statusText;
    const err = new Error(msg || 'Erro na requisição');
    err.status = res.status;
    // Toasts amigáveis por status
    if (res.status >= 500) showToast('Erro no servidor. Tente novamente mais tarde.', 'error');
    else if (res.status === 400) showToast(msg || 'Requisição inválida.', 'error');
    else showToast(msg || 'Erro na requisição.', 'error');
    throw err;
  }
  return data;
}

export const api = {
  get: (path, params) => request(`${path}${buildQuery(params)}`),
  post: (path, payload) => request(path, { method: 'POST', body: payload }),
  put: (path, payload) => request(path, { method: 'PUT', body: payload }),
  delete: (path) => request(path, { method: 'DELETE' }),
};

export const apiUsuarios = {
  list: (params) => api.get('/api/usuarios', params),
  get: (id) => api.get(`/api/usuarios/${id}`),
  create: (payload) => api.post('/api/usuarios', payload),
  update: (id, payload) => api.put(`/api/usuarios/${id}`, payload),
  remove: (id) => api.delete(`/api/usuarios/${id}`),
};

export const apiAgendamentos = {
  list: (params) => api.get('/api/agendamentos', params),
  filter: (params) => api.get('/api/agendamentos/filtro', params),
  get: (id) => api.get(`/api/agendamentos/${id}`),
  create: (payload) => api.post('/api/agendamentos', payload),
  update: (id, payload) => api.put(`/api/agendamentos/${id}`, payload),
  remove: (id) => api.delete(`/api/agendamentos/${id}`),
  chamar: (id) => api.post(`/api/agendamentos/${id}/chamar`, {}),
};

export const apiAtendimentos = {
  list: (params) => api.get('/api/atendimentos', params),
  get: (id) => api.get(`/api/atendimentos/${id}`),
  create: (payload) => api.post('/api/atendimentos', payload),
  update: (id, payload) => api.put(`/api/atendimentos/${id}`, payload),
  remove: (id) => api.delete(`/api/atendimentos/${id}`),
};

export { request as http, buildQuery };
