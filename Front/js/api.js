const API_BASE = localStorage.getItem('sga_api_base') || 'http://127.0.0.1:5000';

function buildQuery(params = {}) {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') q.append(k, v);
  });
  const s = q.toString();
  return s ? `?${s}` : '';
}

async function http(method, path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  const ct = res.headers.get('content-type') || '';
  const data = ct.includes('application/json') ? await res.json() : await res.text();
  if (!res.ok) {
    const msg = typeof data === 'object' && data && data.mensagem ? data.mensagem : res.statusText;
    throw new Error(msg || 'Erro na requisição');
  }
  return data;
}

export const apiUsuarios = {
  list: (params) => http('GET', `/api/usuarios${buildQuery(params)}`),
  get: (id) => http('GET', `/api/usuarios/${id}`),
  create: (payload) => http('POST', `/api/usuarios`, payload),
  update: (id, payload) => http('PUT', `/api/usuarios/${id}`, payload),
  remove: (id) => http('DELETE', `/api/usuarios/${id}`),
};

export const apiAgendamentos = {
  list: (params) => http('GET', `/api/agendamentos${buildQuery(params)}`),
  filter: (params) => http('GET', `/api/agendamentos/filtro${buildQuery(params)}`),
  get: (id) => http('GET', `/api/agendamentos/${id}`),
  create: (payload) => http('POST', `/api/agendamentos`, payload),
  update: (id, payload) => http('PUT', `/api/agendamentos/${id}`, payload),
  remove: (id) => http('DELETE', `/api/agendamentos/${id}`),
};

export const apiAtendimentos = {
  list: (params) => http('GET', `/api/atendimentos${buildQuery(params)}`),
  get: (id) => http('GET', `/api/atendimentos/${id}`),
  create: (payload) => http('POST', `/api/atendimentos`, payload),
  update: (id, payload) => http('PUT', `/api/atendimentos/${id}`, payload),
  remove: (id) => http('DELETE', `/api/atendimentos/${id}`),
};
