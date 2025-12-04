// Auth utilities for SAS front-end
// - Handles JWT login/logout, token storage, route protection and helpers

const BASE_URL = localStorage.getItem('sga_api_base') || 'http://localhost:3000';
const TOKEN_KEY = 'token_sas';
const USER_KEY = 'sas_usuario';
const REMEMBER_KEY = 'sga_remember';
const EXPIRES_AT_KEY = 'token_expires_at';

function decodeJwtPayload(token) {
  try {
    const payload = token.split('.')[1];
    const json = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(decodeURIComponent(Array.prototype.map.call(json, c =>
      '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
    ).join('')));
  } catch (e) { return null; }
}

export function getToken() { return localStorage.getItem(TOKEN_KEY) || ''; }
export function getUser() {
  try { return JSON.parse(localStorage.getItem(USER_KEY) || 'null'); } catch { return null; }
}
export function isLogged() {
  const token = getToken();
  if (!token) return false;
  const expAt = Number(localStorage.getItem(EXPIRES_AT_KEY) || 0);
  if (expAt && Date.now() > expAt) return false;
  return true;
}

export function requireAuth() {
  if (!isLogged()) { window.location.href = 'index.html'; return false; }
  return true;
}

export async function login({ nome, senha, remember }) {
  try {
    // Tenta usar o testAPI se estiver disponível (ambiente de teste)
    if (window.testAPI) {
      console.log('Usando testAPI para login');
      const response = await window.testAPI.login(nome, senha);
      
      // Se chegou aqui, o login foi bem-sucedido
      const token = response.token;
      const usuario = response.usuario;
      
      // Salva os dados no localStorage
      localStorage.setItem(TOKEN_KEY, token);
      if (usuario) {
        localStorage.setItem(USER_KEY, JSON.stringify(usuario));
      }
      
      // Configura o remember-me
      const rememberMs = remember ? 1000 * 60 * 60 * 24 * 30 : 0; // 30 dias
      const expiresAt = Date.now() + (remember ? rememberMs : 1000 * 60 * 60 * 4); // 4h padrão
      localStorage.setItem(EXPIRES_AT_KEY, String(expiresAt));
      localStorage.setItem(REMEMBER_KEY, remember ? '1' : '0');
      
      return { token, usuario, sucesso: true };
    }
    
    // Código original para quando não estiver usando testAPI
    const reqBody = { senha };
    // Se parece um email, usa como email, senão usa como nome
    if (nome.includes('@')) {
      reqBody.email = nome;
    } else {
      reqBody.nome = nome;
    }
    
    const res = await fetch(`${BASE_URL}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reqBody)
    });
    
    const data = await res.json().catch(() => ({}));
    
    if (!res.ok || !data.token) {
      const msg = data?.error || 'Usuário ou senha inválidos';
      const err = new Error(msg);
      throw err;
    }
    
    const token = data.token || '';
    const usuario = data.usuario || (data.id || data.nome ? { id: data.id, nome: data.nome } : null);
    if (!token) throw new Error('Token não recebido');
    
    localStorage.setItem(TOKEN_KEY, token);
    if (usuario) localStorage.setItem(USER_KEY, JSON.stringify(usuario));

    const tokenPayload = decodeJwtPayload(token);
    const jwtExpMs = tokenPayload && tokenPayload.exp ? tokenPayload.exp * 1000 : 0;
    const rememberMs = remember ? 1000 * 60 * 60 * 24 * 30 : 0; // 30 dias
    const expiresAt = jwtExpMs || (Date.now() + (remember ? rememberMs : 1000 * 60 * 60 * 4)); // 4h padrão
    localStorage.setItem(EXPIRES_AT_KEY, String(expiresAt));
    localStorage.setItem(REMEMBER_KEY, remember ? '1' : '0');
    return { token, usuario, sucesso: true };
    
  } catch (error) {
    console.error('Erro no login:', error);
    throw error;
  }
}

export async function logout() {
  try {
    const token = getToken();
    if (token) {
      await fetch(`${BASE_URL}/api/auth/logout`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
    }
  } catch (e) { /* opcional */ }
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(EXPIRES_AT_KEY);
  // manter preferência do remember
}

// Toast simples reutilizável
export function showToast(message, type = 'info') {
  let container = document.getElementById('sas_toast_container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'sas_toast_container';
    container.style.position = 'fixed';
    container.style.top = '16px';
    container.style.right = '16px';
    container.style.zIndex = '9999';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.gap = '8px';
    document.body.appendChild(container);
  }
  const el = document.createElement('div');
  el.textContent = message;
  el.style.padding = '10px 14px';
  el.style.borderRadius = '8px';
  el.style.color = type === 'error' ? '#721c24' : (type === 'success' ? '#0f5132' : '#084298');
  el.style.background = type === 'error' ? '#f8d7da' : (type === 'success' ? '#d1e7dd' : '#cfe2ff');
  el.style.border = '1px solid ' + (type === 'error' ? '#f5c2c7' : (type === 'success' ? '#badbcc' : '#b6d4fe'));
  el.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
  container.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; el.style.transition = 'opacity .4s'; setTimeout(() => el.remove(), 400); }, 3000);
}

// Expose for non-module inline if needed
window.sasAuth = { login, logout, isLogged, requireAuth, getUser, getToken, showToast, BASE_URL };
