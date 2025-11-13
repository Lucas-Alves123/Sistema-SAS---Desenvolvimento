// Atendimento page logic
// - Render list from localStorage
// - Simple call action highlight

import { tryPopulateHeaderUser, initHeaderUserCommon, initReportsMenuClick } from './global.js';
import { apiAtendimentos } from './api.js';

document.addEventListener('DOMContentLoaded', function() {
    if (!window.location.pathname.includes('atendimento.html')) return;
    initHeaderUserCommon();
    initReportsMenuClick();
    renderAtendimentoList();
    populateCurrentServiceFromSchedules();
});

export async function renderAtendimentoList() {
    const listContainer = document.getElementById('attendanceList');
    if (!listContainer) return;
    try {
        const resp = await apiAtendimentos.list({ per_page: 20 });
        const itens = (resp && resp.atendimentos) ? resp.atendimentos.map(a => ({ nome: `Usuário ${a.usuario_id}`, tipo: a.descricao || 'Atendimento' })) : [];
        listContainer.innerHTML = itens.map(renderAttendanceCard).join('');
    } catch (err) {
        const data = getAttendanceData();
        listContainer.innerHTML = data.map(renderAttendanceCard).join('');
    }
    const callNextBtn = document.getElementById('btnCallNext');
    if (callNextBtn) {
        callNextBtn.addEventListener('click', () => { alert('Chamando próximo atendimento...'); });
    }
}

export function renderAttendanceCard(item) {
    return `
        <div class="attendance-card">
            <div class="attendance-card-header">
                <span class="status-dot">🟡</span>
                <span class="attendance-name">${item.nome}</span>
            </div>
            <div class="attendance-card-body">
                <div class="attendance-info">
                    <div><strong>Tipo de serviço:</strong> ${item.tipo}</div>
                    <div class="status-badge">🔴 Encerrado</div>
                </div>
                <div class="attendance-actions-inline">
                    <button class="btn-primary btn-megaphone" onclick="handleCallOne(this)">📣 Chamar</button>
                </div>
            </div>
        </div>`;
}

export function getAttendanceData() {
    const saved = JSON.parse(localStorage.getItem('sas_schedules') || '[]');
    if (saved.length > 0) {
        return saved.map(s => ({ nome: s.fullName || 'Servidor', tipo: s.serviceType || 'Atendimento Geral' })).reverse();
    }
    return [
        { nome: 'Ana Beatriz Santos', tipo: 'Seleção Pública Simplificada' },
        { nome: 'Carlos Henrique', tipo: 'Pagamento' },
        { nome: 'Mariana Costa', tipo: 'Licença' }
    ];
}

export function populateCurrentServiceFromSchedules() {
    const info = document.getElementById('currentServiceInfo');
    const nameSpan = document.getElementById('currentName');
    const serviceSpan = document.getElementById('currentService');
    if (!info || !nameSpan || !serviceSpan) return;
    const saved = JSON.parse(localStorage.getItem('sas_schedules') || '[]');
    if (saved.length === 0) return;
    const last = saved[saved.length - 1];
    nameSpan.textContent = last.fullName || '';
    serviceSpan.textContent = last.serviceType || '';
    info.style.display = 'block';
}

// Expose for inline onclick
window.handleCallOne = function(btn) {
    const card = btn.closest('.attendance-card');
    if (!card) return;
    card.style.boxShadow = '0 0 0 3px rgba(0, 51, 160, 0.25)';
    setTimeout(() => { card.style.boxShadow = ''; }, 1200);
}


