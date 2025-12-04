// Atendimento page logic
// - Lista fila via API com polling
// - Chamar próximo/um e feedback visual/sonoro

import { tryPopulateHeaderUser, initHeaderUserCommon, initReportsMenuClick } from './global.js';
import { apiAgendamentos, apiAtendimentos } from './api.js';
import { requireAuth, showToast, getUser } from './auth.js';

let pollingTimer = null;

document.addEventListener('DOMContentLoaded', function() {
    if (!window.location.pathname.includes('atendimento.html')) return;
    // Em modo local (file://) permitir sem autenticação para demonstrar fluxo
    if (window.location.protocol !== 'file:') {
        if (!requireAuth()) return;
    }

function isInternalUser() {
    try {
        const u = getUser();
        const name = (u?.nome || '').trim().toLowerCase();
        // Heurística temporária: qualquer usuário autenticado interno do sistema (não cliente público)
        return Boolean(name);
    } catch(_) { return false; }
}

function formatHHmm(iso) {
    try { const d = new Date(iso); const hh = String(d.getHours()).padStart(2,'0'); const mm = String(d.getMinutes()).padStart(2,'0'); return `${hh}:${mm}`; } catch { return ''; }
}

function ensureEndTimeLabel(cardEl) {
    if (!cardEl) return { textContent: '' };
    const infoRight = cardEl.querySelector('.attendance-card-body .attendance-info:last-child');
    if (!infoRight) return { textContent: '' };
    let el = infoRight.querySelector('.end-time-label');
    if (!el) {
        el = document.createElement('div');
        el.className = 'end-time-label';
        el.style.opacity = '.8';
        infoRight.appendChild(el);
    }
    return el;
}

function initDeskBadge(){
    try {
        const badge = document.getElementById('deskBadge');
        const numEl = document.getElementById('deskNumber');
        if (!badge || !numEl) return;
        const storageKey = 'sas_desk_number';
        const saved = parseInt(localStorage.getItem(storageKey) || '1', 10) || 1;
        numEl.textContent = String(saved);
        badge.addEventListener('click', () => {
            const current = parseInt(numEl.textContent || '1', 10) || 1;
            const value = prompt('Informe o número do guichê (ex.: 1, 2, 3):', String(current));
            if (value === null) return;
            const n = Math.max(1, Math.min(99, parseInt(value, 10) || current));
            numEl.textContent = String(n);
            localStorage.setItem(storageKey, String(n));
        });
    } catch(_) {}
}
    initHeaderUserCommon();
    initReportsMenuClick();
    bindHeaderActions();
    showLocalCurrent();
    // consumo imediato de item pendente vindo do agendamento (após redirect)
    try {
        const pendRaw = sessionStorage.getItem('sas_pending_render');
        if (pendRaw) {
            const pend = JSON.parse(pendRaw);
            if (pend && pend.nome) {
                const qKey = 'sas_queue';
                const lst = JSON.parse(localStorage.getItem(qKey) || '[]');
                lst.push({ ...pend, ts: Date.now() });
                localStorage.setItem(qKey, JSON.stringify(lst));
            }
            sessionStorage.removeItem('sas_pending_render');
        }
    } catch(_) {}
    loadAndRenderQueue();
    startPolling();
    initDeskBadge();
});

function startPolling() {
    stopPolling();
    pollingTimer = setInterval(() => { loadAndRenderQueue(); showLocalCurrent(); }, 7000);
}

async function encerrarAtendimento(id, cardEl) {
    try {
        // Se houver endpoint específico, pode-se ajustar aqui. Usando PUT como contrato.
        const endedAtISO = new Date().toISOString();
        await apiAgendamentos.update(id, { status: 'concluido', data_fim: endedAtISO });
        flashCard(cardEl);
        showToast('Atendimento finalizado!', 'success');
        // Apenas perfis internos visualizam horário de término
        try {
            if (isInternalUser()) {
                const endLabel = ensureEndTimeLabel(cardEl);
                endLabel.textContent = `Término: ${formatHHmm(endedAtISO)}`;
            }
        } catch(_) {}
        await loadAndRenderQueue();
    } catch (e) {
        showToast(e?.message || 'Falha ao encerrar atendimento', 'error');
    }
    // reforça exibição local após renderizações
    showLocalCurrent();
}
function stopPolling() { if (pollingTimer) clearInterval(pollingTimer); pollingTimer = null; }

async function loadAndRenderQueue() {
    const listContainer = document.getElementById('attendanceList');
    if (!listContainer) return;
    try {
        // Preferir agendamentos com status=agendado
        const resp = await apiAgendamentos.list({ status: 'agendado', per_page: 50 });
        let items = normalizeAgendamentos(resp);
        // Merge com dados locais para exibição imediata do último agendamento
        const localItems = getAttendanceData();
        items = mergeUniqueAttendances(items, localItems);
        listContainer.innerHTML = items.map(renderAttendanceCard).join('');
        attachCardActions(items);
        updateWaitingCounter(items);
    } catch (e) {
        // fallback local
        const data = getAttendanceData();
        listContainer.innerHTML = data.map(renderAttendanceCard).join('');
        attachCardActions(data);
        updateWaitingCounter(data);
    }

    const callNextBtn = document.getElementById('btnCallNext');
    if (callNextBtn && !callNextBtn.dataset.bound) {
        callNextBtn.dataset.bound = '1';
        callNextBtn.addEventListener('click', async () => {
            showToast('Chamando próximo…', 'info');
            await handleCallNext();
        });
    }
}

function normalizeAgendamentos(resp) {
    const arr = Array.isArray(resp) ? resp : (resp?.agendamentos || resp?.items || []);
    return arr.map(a => ({
        id: a.id,
        nome: a.nome_completo || a.nome || 'Servidor',
        tipo: a.tipo_servico || a.tipo || 'Atendimento',
        prioridade: a.prioridade || 'Normal',
        hora: a.hora_inicio || a.horario || '',
        status: (a.status || 'agendado').toLowerCase()
    }));
}

function statusVisual(status) {
    const s = (status || '').toLowerCase();
    if (s === 'agendado' || s === 'pendente') return { emoji: '🔴', color: '#dc3545', label: 'Aguardando' };
    if (s === 'em_atendimento' || s === 'andamento') return { emoji: '🟡', color: '#ffc107', label: 'Em atendimento' };
    if (s === 'concluido' || s === 'concluído' || s === 'finalizado') return { emoji: '🟢', color: '#28a745', label: 'Concluído' };
    return { emoji: '🔵', color: '#0d6efd', label: 'Status' };
}

function renderAttendanceCard(item) {
    const prioridade = (item.prioridade || '').toLowerCase();
    const badge = prioridade === 'urgente' ? 'Prioridade: urgente' : 'Prioridade: normal';
    const vis = statusVisual(item.status);
    const borderStyle = `style="border-left: 4px solid ${vis.color};"`;
    const statusClass = (function(s){
        s = (s||'').toLowerCase();
        if (s==='concluido' || s==='concluído' || s==='finalizado') return 'is-concluded';
        if (s==='em_atendimento' || s==='andamento') return 'is-progress';
        return 'is-waiting';
    })(item.status);
    const rightLabel = (statusClass==='is-concluded') ? 'Atendido' : (vis.label);
    return `
        <div class="attendance-card ${statusClass}" data-id="${item.id || ''}" ${borderStyle}>
            <div class="attendance-card-header">
                <span class="attendance-name">${item.nome}</span>
            </div>
            <div class="attendance-card-body">
                <div class="attendance-info">
                    <div><strong>Tipo de serviço:</strong> ${item.tipo}</div>
                    <div><strong>Horário:</strong> ${item.hora || '-'}</div>
                </div>
                <div class="attendance-info" style="text-align:right; min-width:160px;">
                    <div style="font-weight:700;">${rightLabel}</div>
                    <div style="opacity:.9;">${badge}</div>
                    ${isInternalUser() ? '<div class="end-time-label" style="opacity:.8;"></div>' : ''}
                </div>
            </div>
            ${statusClass==='is-concluded' ? '' : `
            <div class="attendance-actions-inline" style="margin-top:10px;">
                <button class="btn-primary btn-megaphone js-call-one">📣 Chamar</button>
                <button class="btn-secondary js-end-one">✅ Encerrar Atendimento</button>
            </div>`}
        </div>`;
}

function attachCardActions(items) {
    document.querySelectorAll('.attendance-card .js-call-one').forEach(btn => {
        if (btn.dataset.bound) return;
        btn.dataset.bound = '1';
        btn.addEventListener('click', async (e) => {
            const card = e.currentTarget.closest('.attendance-card');
            const id = card?.dataset?.id;
            if (!id) return;
            await chamarAgendamento(id, card);
        });
    });
    document.querySelectorAll('.attendance-card .js-end-one').forEach(btn => {
        if (btn.dataset.bound) return;
        btn.dataset.bound = '1';
        btn.addEventListener('click', async (e) => {
            const card = e.currentTarget.closest('.attendance-card');
            const id = card?.dataset?.id;
            if (!id) return;
            await encerrarAtendimento(id, card);
        });
    });
}

async function handleCallNext() {
    const firstCard = document.querySelector('.attendance-card');
    if (!firstCard) { showToast('Fila vazia.', 'info'); return; }
    const id = firstCard.dataset.id;
    await chamarAgendamento(id, firstCard);
}

async function chamarAgendamento(id, cardEl) {
    try {
        try {
            await apiAgendamentos.chamar(id);
        } catch (_) {
            // fallback se /chamar não existir
            await apiAgendamentos.update(id, { status: 'em_atendimento', data_inicio: new Date().toISOString() });
        }
        flashCard(cardEl);
        playDing();
        showToast('Chamando atendimento...', 'success');
        // Atualiza lista após chamar
        await loadAndRenderQueue();
    } catch (e) {
        showToast(e?.message || 'Falha ao chamar atendimento', 'error');
    }
}

function flashCard(card) {
    if (!card) return;
    card.style.boxShadow = '0 0 0 3px rgba(0, 51, 160, 0.25)';
    setTimeout(() => { card.style.boxShadow = ''; }, 1200);
}

function playDing() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.connect(g); g.connect(ctx.destination);
        o.type = 'sine'; o.frequency.value = 880;
        g.gain.setValueAtTime(0.001, ctx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.2, ctx.currentTime + 0.01);
        o.start();
        setTimeout(() => { g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.2); o.stop(ctx.currentTime + 0.21); }, 180);
    } catch {}
}

function getAttendanceData() {
    // Itens leves em fila (exibição imediata após agendar)
    let queue = [];
    try { queue = JSON.parse(localStorage.getItem('sas_queue') || '[]'); } catch (_) { queue = []; }
    const qItems = (queue || []).map(it => ({
        nome: it.nome || 'Servidor',
        tipo: it.tipo || 'Atendimento',
        hora: it.hora || '',
        status: (it.status || 'agendado').toLowerCase()
    }));

    // Histórico completo para fallback
    let saved = [];
    try { saved = JSON.parse(localStorage.getItem('sas_schedules') || '[]'); } catch(_) { saved = []; }
    const sItems = (saved || []).map(s => ({
        nome: s.fullName || 'Servidor',
        tipo: s.serviceType || 'Atendimento Geral',
        hora: s.startTime || '',
        status: 'agendado'
    })).reverse();

    return mergeUniqueAttendances(qItems, sItems);
}

function mergeUniqueAttendances(primary, secondary) {
    // De-dup por chave composta (nome+tipo+hora) para evitar duplicatas visuais
    const seen = new Set();
    const out = [];
    const pushIfNew = (it) => {
        const key = `${(it.nome||'').trim()}|${(it.tipo||'').trim()}|${(it.hora||'').trim()}`.toLowerCase();
        if (seen.has(key)) return;
        seen.add(key);
        out.push(it);
    };
    (primary || []).forEach(pushIfNew);
    (secondary || []).forEach(pushIfNew);
    return out;
}

function bindHeaderActions() {
    const info = document.getElementById('currentServiceInfo');
    const nameSpan = document.getElementById('currentName');
    const serviceSpan = document.getElementById('currentService');
    if (!info || !nameSpan || !serviceSpan) return;
    // Preencher com último da lista local (indicativo)
    const saved = JSON.parse(localStorage.getItem('sas_schedules') || '[]');
    if (saved.length === 0) return;
    const last = saved[saved.length - 1];
    nameSpan.textContent = last.fullName || '';
    serviceSpan.textContent = last.serviceType || '';
    info.style.display = 'block';
}

function showLocalCurrent() {
    try {
        const info = document.getElementById('currentServiceInfo');
        const nameSpan = document.getElementById('currentName');
        const serviceSpan = document.getElementById('currentService');
        if (!info || !nameSpan || !serviceSpan) return;
        const saved = JSON.parse(localStorage.getItem('sas_schedules') || '[]');
        if (!saved.length) return;
        const last = saved[saved.length - 1];
        if (last) {
            if (nameSpan.textContent !== (last.fullName || '')) nameSpan.textContent = last.fullName || '';
            if (serviceSpan.textContent !== (last.serviceType || '')) serviceSpan.textContent = last.serviceType || '';
            if (info.style.display === 'none') info.style.display = 'block';
        }
    } catch (_) {}
}

// Expose for debug if needed
window.sasAtendimento = { loadAndRenderQueue };


