import { apiUsuarios } from './api.js';
import { requireAuth, getUser, showToast } from './auth.js';
import { initHeaderUserCommon } from './global.js';

const PAGE_SIZE = 10;
let state = { page: 1, total: 0, pages: 1, filterStatus: '', filterTipo: '' };

function getCurrentUserTipo() {
  try {
    const u = getUser();
    // Preferir tipo vindo do backend no objeto usuario
    if (u && u.tipo) return String(u.tipo).toUpperCase();
    // Fallback opcional: chave local caso backend ainda não envie
    const local = localStorage.getItem('sas_usuario_tipo');
    if (local) return String(local).toUpperCase();
  } catch(_) {}
  return '';
}

function isAdminTemp() {
  // Enquanto não há controle real, permitir acesso à página, mas privilégios dependem do tipo
  const u = getUser();
  return Boolean(u); // qualquer logado entra na página; regras finas abaixo
}

function tipoToLabel(tipo) {
  const t = String(tipo || '').toUpperCase();
  if (t === 'DEV') return 'DEV';
  if (t === 'ADM') return 'ADM';
  return 'USER';
}

function ativoToLabel(v) { return v ? 'Ativo' : 'Inativo'; }

function bindHeader() { initHeaderUserCommon(); }

function bindFilters() {
  const btn = document.getElementById('btnFiltros');
  const panel = document.getElementById('filtersPanel');
  const fxStatus = document.getElementById('fxStatus');
  const fxTipo = document.getElementById('fxTipo');
  if (btn) btn.addEventListener('click', () => {
    if (!panel) return;
    panel.style.display = panel.style.display === 'none' || !panel.style.display ? 'block' : 'none';
  });
  const applyIfReady = () => {
    const s = fxStatus?.value || '';
    const t = fxTipo?.value || '';
    state.filterStatus = s;
    state.filterTipo = t;
    if (s && t) { state.page = 1; loadGrid(); }
  };
  if (fxStatus && !fxStatus.dataset.bound) { fxStatus.dataset.bound = '1'; fxStatus.addEventListener('change', applyIfReady); }
  if (fxTipo && !fxTipo.dataset.bound) { fxTipo.dataset.bound = '1'; fxTipo.addEventListener('change', applyIfReady); }
}

function bindPagination() {
  const prev = document.getElementById('prevPage');
  const next = document.getElementById('nextPage');
  if (prev) prev.addEventListener('click', () => { if (state.page > 1) { state.page--; loadGrid(); } });
  if (next) next.addEventListener('click', () => { if (state.page < state.pages) { state.page++; loadGrid(); } });
}

function bindNovoUsuario() {
  const btn = document.getElementById('btnNovo');
  if (!btn) return;
  btn.addEventListener('click', () => openCreateDialog());
}

function renderRows(list) {
  const tbody = document.getElementById('gridUsuarios');
  if (!tbody) return;
  tbody.innerHTML = '';
  list.forEach(u => {
    const tr = document.createElement('tr');
    const tipo = tipoToLabel(u.tipo);
    const tipoHtml = tipo === 'DEV'
      ? `<span style="display:inline-block;background:#1e293b;color:#fff;border-radius:999px;padding:2px 8px;font-size:12px;font-weight:600;">DEV</span>`
      : `<span style="display:inline-block;background:#E6EBF5;color:#0033A0;border-radius:999px;padding:2px 8px;font-size:12px;font-weight:600;">${tipo}</span>`;
    tr.innerHTML = `
      <td style="padding:10px;border-bottom:1px solid #f0f0f0;">${u.id}</td>
      <td style="padding:10px;border-bottom:1px solid #f0f0f0;">${u.nome || ''}</td>
      <td style="padding:10px;border-bottom:1px solid #f0f0f0;">${ativoToLabel(u.ativo)}</td>
      <td style="padding:10px;border-bottom:1px solid #f0f0f0;">${tipoHtml}</td>
      <td style="padding:10px;border-bottom:1px solid #f0f0f0;">
        <div style="display:flex;gap:8px;justify-content:flex-end;">
          <button class="btn-edit" data-id="${u.id}" title="Editar" style="background:#fff;border:1px solid #ddd;border-radius:6px;padding:6px 10px;cursor:pointer;"><i class="fa-solid fa-pen"></i></button>
          <button class="btn-del" data-id="${u.id}" title="Excluir" style="background:#fff;border:1px solid #ddd;border-radius:6px;padding:6px 10px;cursor:pointer;color:#B00020;"><i class="fa-solid fa-trash"></i></button>
        </div>
      </td>`;
    tbody.appendChild(tr);
    // Permissões: DEV só editável por DEV
    const userTipo = getCurrentUserTipo();
    if (tipo === 'DEV' && userTipo !== 'DEV') {
      const editBtn = tr.querySelector('.btn-edit');
      const delBtn = tr.querySelector('.btn-del');
      if (editBtn) { editBtn.disabled = true; editBtn.style.opacity = '.5'; editBtn.title = 'Somente DEV pode editar DEV'; }
      if (delBtn) { delBtn.disabled = true; delBtn.style.opacity = '.5'; delBtn.title = 'Somente DEV pode excluir DEV'; }
    }
  });
  tbody.querySelectorAll('.btn-edit').forEach(btn => btn.addEventListener('click', () => openEditDialog(btn.dataset.id)));
  tbody.querySelectorAll('.btn-del').forEach(btn => btn.addEventListener('click', () => onDelete(btn.dataset.id)));
}

function renderPagination(total, page, pages) {
  const info = document.getElementById('pageInfo');
  if (info) info.textContent = `Página ${page} de ${pages} (Total: ${total})`;
}

async function loadGrid() {
  const params = { page: state.page, per_page: PAGE_SIZE };
  try {
    // Requer filtros definidos; caso contrário, mostrar painel e não carregar
    if (!state.filterStatus || !state.filterTipo) {
      const panel = document.getElementById('filtersPanel');
      if (panel) panel.style.display = 'block';
      const tbody = document.getElementById('gridUsuarios');
      if (tbody) tbody.innerHTML = '';
      const info = document.getElementById('pageInfo');
      if (info) info.textContent = 'Selecione Situação e Tipo para listar usuários';
      return;
    }
    const resp = await apiUsuarios.list(params);
    let items = resp.usuarios || resp.items || [];
    // client-side filters (Situação e Tipo) - obrigatórios
    if (state.filterStatus) items = items.filter(i => String(!!i.ativo) === String(state.filterStatus === 'ATIVO'));
    if (state.filterTipo) items = items.filter(i => tipoToLabel(i.tipo) === state.filterTipo);
    // sort by ID asc
    items.sort((a,b) => (a.id||0) - (b.id||0));
    const total = items.length;
    const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    const start = (state.page - 1) * PAGE_SIZE;
    const pageItems = items.slice(start, start + PAGE_SIZE);
    state.total = total; state.pages = pages;
    renderRows(pageItems);
    renderPagination(total, state.page, pages);
  } catch (e) {
    console.error(e);
  }
}

function ensureAdminAccess() {
  if (!isAdminTemp()) {
    showToast('Acesso restrito a administradores.', 'error');
    setTimeout(() => { window.location.href = 'home.html'; }, 600);
    return false;
  }
  return true;
}

function openEditDialog(id) {
  const modal = buildModal();
  modal.title.textContent = 'Editar Usuário';
  const form = buildForm();
  modal.body.appendChild(form.el);
  modal.show();
  // carregar dados
  apiUsuarios.get(id).then(data => {
    const u = data.usuario || data;
    form.nome.value = u.nome || '';
    form.email.value = u.email || '';
    form.status.value = (!!u.ativo) ? 'true' : 'false';
    form.tipo.value = tipoToLabel(u.tipo);
    // Bloquear edição se alvo for DEV e operador não for DEV
    const currentTipo = getCurrentUserTipo();
    const targetTipo = tipoToLabel(u.tipo);
    if (targetTipo === 'DEV' && currentTipo !== 'DEV') {
      form.nome.disabled = true; form.email.disabled = true; form.senha.disabled = true; form.status.disabled = true; form.tipo.disabled = true;
      modal.title.textContent = 'Visualizar Usuário (somente DEV pode editar DEV)';
    }
  }).catch(()=>{});
  modal.onSave = async () => {
    // Revalida permissão ao salvar
    const currentTipo = getCurrentUserTipo();
    if (form.tipo.value === 'DEV' && currentTipo !== 'DEV') { showToast('Somente DEV pode editar DEV.', 'error'); return; }
    const payload = {};
    if (form.nome.value) payload.nome = form.nome.value;
    if (form.email.value) payload.email = form.email.value;
    if (form.senha.value) payload.senha = form.senha.value;
    if (form.status.value !== '') payload.ativo = form.status.value === 'true';
    if (form.tipo.value) payload.tipo = form.tipo.value;
    await apiUsuarios.update(id, payload);
    showToast('Usuário atualizado.', 'success');
    modal.close();
    loadGrid();
  };
}

function openCreateDialog() {
  const modal = buildModal();
  modal.title.textContent = 'Novo Usuário';
  const form = buildForm(true);
  modal.body.appendChild(form.el);
  modal.show();
  modal.onSave = async () => {
    const payload = {
      nome: form.nome.value,
      email: form.email.value,
      senha: form.senha.value,
      ativo: form.status.value === 'true',
      tipo: form.tipo.value
    };
    if (!payload.nome || !payload.email || !payload.senha || !payload.tipo) {
      showToast('Preencha nome, e-mail, senha e tipo.', 'error');
      return;
    }
    await apiUsuarios.create(payload);
    showToast('Usuário criado.', 'success');
    modal.close();
    loadGrid();
  };
}

async function onDelete(id) {
  // Buscar para checar tipo e bloquear DEV
  try {
    const data = await apiUsuarios.get(id);
    const u = data.usuario || data;
    const targetTipo = tipoToLabel(u.tipo);
    const currentTipo = getCurrentUserTipo();
    if (targetTipo === 'DEV' && currentTipo !== 'DEV') { showToast('Somente DEV pode excluir DEV.', 'error'); return; }
  } catch(_){ }
  if (!confirm('Tem certeza que deseja excluir este usuário? Esta ação não pode ser desfeita.')) return;
  await apiUsuarios.remove(id);
  showToast('Usuário excluído.', 'success');
  loadGrid();
}

function buildModal() {
  let overlay = document.createElement('div');
  overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.35);display:flex;align-items:center;justify-content:center;z-index:9999;';
  let box = document.createElement('div');
  box.style.cssText = 'background:#fff;border-radius:12px;min-width:320px;max-width:560px;width:90%;box-shadow:0 10px 40px rgba(0,0,0,.12);overflow:hidden;';
  let header = document.createElement('div');
  header.style.cssText = 'display:flex;align-items:center;justify-content:space-between;padding:14px 16px;border-bottom:1px solid #eee;';
  let title = document.createElement('h3');
  title.style.cssText = 'margin:0;font-size:18px;color:#0033A0;';
  let btnClose = document.createElement('button');
  btnClose.innerHTML = '&times;';
  btnClose.style.cssText = 'background:transparent;border:none;font-size:22px;cursor:pointer;';
  let body = document.createElement('div');
  body.style.cssText = 'padding:16px;';
  let footer = document.createElement('div');
  footer.style.cssText = 'display:flex;gap:10px;justify-content:flex-end;padding:12px 16px;border-top:1px solid #eee;';
  let btnBack = document.createElement('button');
  btnBack.textContent = 'Voltar';
  btnBack.style.cssText = 'background:#fff;border:1px solid #ddd;border-radius:8px;padding:10px 14px;cursor:pointer;';
  let btnSave = document.createElement('button');
  btnSave.textContent = 'Salvar';
  btnSave.style.cssText = 'background:#0033A0;color:#fff;border:none;border-radius:8px;padding:10px 16px;cursor:pointer;';

  header.appendChild(title);
  header.appendChild(btnClose);
  box.appendChild(header);
  box.appendChild(body);
  footer.appendChild(btnBack);
  footer.appendChild(btnSave);
  box.appendChild(footer);
  overlay.appendChild(box);

  const api = {
    title,
    body,
    show() { document.body.appendChild(overlay); },
    close() { overlay.remove(); },
    onSave: null
  };
  btnClose.addEventListener('click', api.close);
  btnBack.addEventListener('click', api.close);
  btnSave.addEventListener('click', () => api.onSave && api.onSave());
  return api;
}

function buildForm(requireAll = false) {
  const el = document.createElement('form');
  el.innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
      <div style="display:flex;flex-direction:column;gap:6px;">
        <label>Usuário (nome)</label>
        <input id="fNome" type="text" ${requireAll ? 'required' : ''} style="padding:10px 12px;border:1px solid #ddd;border-radius:8px;"/>
      </div>
      <div style="display:flex;flex-direction:column;gap:6px;">
        <label>E-mail</label>
        <input id="fEmail" type="email" ${requireAll ? 'required' : ''} style="padding:10px 12px;border:1px solid #ddd;border-radius:8px;"/>
      </div>
      <div style="display:flex;flex-direction:column;gap:6px;">
        <label>Tipo</label>
        <select id="fTipo" ${requireAll ? 'required' : ''} style="padding:10px 12px;border:1px solid #ddd;border-radius:8px;">
          <option value="USER">USER</option>
          <option value="ADM">ADM</option>
          <option value="DEV">DEV</option>
        </select>
      </div>
      <div style="display:flex;flex-direction:column;gap:6px;">
        <label>Senha</label>
        <input id="fSenha" type="password" ${requireAll ? 'required' : ''} style="padding:10px 12px;border:1px solid #ddd;border-radius:8px;"/>
      </div>
      <div style="display:flex;flex-direction:column;gap:6px;">
        <label>Situação</label>
        <select id="fStatus" ${requireAll ? 'required' : ''} style="padding:10px 12px;border:1px solid #ddd;border-radius:8px;">
          <option value="true">Ativo</option>
          <option value="false">Inativo</option>
        </select>
      </div>
    </div>`;
  return {
    el,
    get nome() { return el.querySelector('#fNome'); },
    get email() { return el.querySelector('#fEmail'); },
    get tipo() { return el.querySelector('#fTipo'); },
    get senha() { return el.querySelector('#fSenha'); },
    get status() { return el.querySelector('#fStatus'); },
  };
}

function openFiltersDialog() {
  const modal = buildModal();
  modal.title.textContent = 'Filtros';
  const wrap = document.createElement('div');
  wrap.innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
      <div style="display:flex;flex-direction:column;gap:6px;">
        <label>Situação</label>
        <select id="fxStatus" required style="padding:10px 12px;border:1px solid #ddd;border-radius:8px;">
          <option value="" disabled selected>Selecione</option>
          <option value="ATIVO">Ativo</option>
          <option value="INATIVO">Inativo</option>
        </select>
      </div>
      <div style="display:flex;flex-direction:column;gap:6px;">
        <label>Tipo</label>
        <select id="fxTipo" required style="padding:10px 12px;border:1px solid #ddd;border-radius:8px;">
          <option value="" disabled selected>Selecione</option>
          <option value="USER">USER</option>
          <option value="ADM">ADM</option>
          <option value="DEV">DEV</option>
        </select>
      </div>
    </div>`;
  modal.body.appendChild(wrap);
  modal.show();
  modal.onSave = () => {
    const s = wrap.querySelector('#fxStatus').value;
    const t = wrap.querySelector('#fxTipo').value;
    if (!s || !t) { showToast('Selecione Situação e Tipo.', 'error'); return; }
    state.filterStatus = s; // ATIVO | INATIVO
    state.filterTipo = t;   // USER | ADM | DEV
    state.page = 1;
    modal.close();
    loadGrid();
  };
}

function boot() {
  if (!requireAuth()) return;
  bindHeader();
  if (!ensureAdminAccess()) return;
  bindFilters();
  bindPagination();
  bindNovoUsuario();
  loadGrid();
}

document.addEventListener('DOMContentLoaded', () => {
  if (window.location.pathname.includes('usuarios.html')) boot();
});
