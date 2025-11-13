// Agendamento page logic
// - Form validation, masks, and field states
// - Protocol generation and persistence
// - Wait time computation

import { tryPopulateHeaderUser, initHeaderUserCommon, initReportsMenuClick } from './global.js';
import { apiAgendamentos } from './api.js';

document.addEventListener('DOMContentLoaded', function() {
    const scheduleForm = document.getElementById('scheduleForm');
    if (!scheduleForm) return;

    initHeaderUserCommon();
    initReportsMenuClick();
    initSchedulePage();

    scheduleForm.addEventListener('submit', handleScheduleSubmit);
    const startDateField = document.getElementById('startDate');
    const startTimeField = document.getElementById('startTime');
    const endTimeField = document.getElementById('endTime');
    const priorityField = document.getElementById('priority');
    const attendanceTypeField = document.getElementById('attendanceType');
    const cpfField = document.getElementById('cpf');
    const registrationField = document.getElementById('registration');
    const emailField = document.getElementById('email');
    const clearFormBtn = document.getElementById('clearForm');

    if (startDateField) startDateField.addEventListener('change', updateWaitTime);
    if (startTimeField) startTimeField.addEventListener('change', handleStartTimeChange);
    if (endTimeField) endTimeField.addEventListener('change', validateEndTime);
    if (priorityField) priorityField.addEventListener('change', handlePriorityChange);
    if (attendanceTypeField) attendanceTypeField.addEventListener('change', handleAttendanceTypeChange);
    if (cpfField) cpfField.addEventListener('input', handleCpfMaskAndValidate);
    if (registrationField) registrationField.addEventListener('input', allowOnlyDigits);
    if (emailField) emailField.addEventListener('input', validateEmailField);
    if (clearFormBtn) clearFormBtn.addEventListener('click', function(e){
        e.preventDefault();
        console.debug('[agendamento] clearForm clicked');
        clearScheduleForm();
    });
    else {
        // fallback: attach delegated listener in case the button is created later
        document.addEventListener('click', function(ev) {
            const target = ev.target;
            if (target && (target.id === 'clearForm' || target.closest && target.closest('#clearForm'))) {
                ev.preventDefault();
                console.debug('[agendamento] delegated clearForm click detected');
                clearScheduleForm();
            }
        });
    }
    const exportBtn = document.getElementById('exportXls');
    if (exportBtn) exportBtn.addEventListener('click', exportSchedulesToXLS);
});

export function initSchedulePage() {
    const now = new Date();
    const dateStr = now.toISOString().slice(0, 10);
    const startDate = document.getElementById('startDate');
    const startTime = document.getElementById('startTime');
    const endTime = document.getElementById('endTime');
    if (startDate && !startDate.value) startDate.value = dateStr;
    if (startTime) {
        if (!startTime.value) startTime.value = '';
        startTime.min = '08:00';
        startTime.max = '16:45';
    }
    if (endTime) {
        if (!endTime.value) endTime.value = '';
        endTime.max = '17:00';
    }
    generateAndSetProtocol();
    updateWaitTime();
    handleAttendanceTypeChange();
}

// Clear all form fields, remove validation states and generated values
export function clearScheduleForm() {
    const form = document.getElementById('scheduleForm');
    if (!form) return;
    console.debug('[agendamento] clearScheduleForm running');
    // Reset native defaults first
    form.reset();
    // Then explicitly clear all inputs/selects/textareas to ensure nothing remains (including disabled/readonly fields)
    const fields = form.querySelectorAll('input, select, textarea');
    fields.forEach(f => {
        const tag = f.tagName.toLowerCase();
        const type = (f.type || '').toLowerCase();
        if (type === 'checkbox' || type === 'radio') {
            f.checked = false;
        } else {
            // clear value for all other input types (including disabled/readonly)
            try { f.value = ''; } catch (_) {}
        }
        // remove validation state
        const group = f.closest('.form-group');
        if (group) {
            group.classList.remove('invalid');
            const small = group.querySelector('.error-text');
            if (small) small.textContent = '';
        }
    });

    // Hide conditional rows
    const justRow = document.getElementById('justificationRow');
    if (justRow) justRow.style.display = 'none';

    // Ensure computed/generated fields are cleared
    const waitField = document.getElementById('waitTime'); if (waitField) waitField.value = '';
    const protocol = document.getElementById('protocol'); if (protocol) protocol.value = '';

    // Focus first input
    const first = form.querySelector('input, select, textarea');
    if (first) first.focus();
}

// Generate unique daily protocol like SAS-YYYYMMDD-XXX
export function generateAndSetProtocol() {
    const protocolEl = document.getElementById('protocol');
    if (!protocolEl) return;
    const today = new Date();
    const y = today.getFullYear();
    const m = String(today.getMonth() + 1).padStart(2, '0');
    const d = String(today.getDate()).padStart(2, '0');
    const key = `sas_protocol_counter_${y}${m}${d}`;
    const next = (parseInt(localStorage.getItem(key) || '0', 10) + 1);
    localStorage.setItem(key, String(next));
    const code = `SAS-${y}${m}${d}-${String(next).padStart(3, '0')}`;
    protocolEl.value = code;
}

// Compute wait time between now and selected datetime
export function updateWaitTime() {
    const waitField = document.getElementById('waitTime');
    const dateEl = document.getElementById('startDate');
    const timeEl = document.getElementById('startTime');
    if (!waitField || !dateEl || !timeEl || !dateEl.value || !timeEl.value) return;
    const selected = new Date(`${dateEl.value}T${timeEl.value}:00`);
    const now = new Date();
    let diffMs = selected.getTime() - now.getTime();
    const sign = diffMs < 0 ? '-' : '';
    diffMs = Math.abs(diffMs);
    const mins = Math.floor(diffMs / 60000);
    const hours = Math.floor(mins / 60);
    const rem = mins % 60;
    waitField.value = `${sign}${String(hours).padStart(2, '0')}h${String(rem).padStart(2, '0')}m`;
}

// Enforce start time constraints and recompute wait/end
export function handleStartTimeChange() {
    const startTime = document.getElementById('startTime');
    if (!startTime || !startTime.value) return;
    const [hStr, mStr] = startTime.value.split(':');
    let h = parseInt(hStr, 10);
    let m = parseInt(mStr, 10);
    if (h < 8) { h = 8; m = 0; }
    if (h > 16) { h = 16; m = 45; }
    if (h === 16 && m > 45) m = 45;
    const hh = String(h).padStart(2, '0');
    const mm = String(m).padStart(2, '0');
    const normalized = `${hh}:${mm}`;
    if (normalized !== startTime.value) startTime.value = normalized;
    updateWaitTime();
    // Auto-adjust end time to be at least +30m and not exceed 17:00
    const endTime = document.getElementById('endTime');
    if (endTime) {
        const minEnd = addMinutesToTime(startTime.value, 30);
        endTime.value = minEnd > '17:00' ? '17:00' : minEnd;
    }
}

export function validateEndTime() {
    const startTime = document.getElementById('startTime');
    const endTime = document.getElementById('endTime');
    if (!startTime || !endTime || !startTime.value || !endTime.value) return;
    const minEnd = addMinutesToTime(startTime.value, 30);
    if (endTime.value <= startTime.value || endTime.value < minEnd) {
        endTime.value = minEnd;
    }
    if (endTime.value > '17:00') {
        endTime.value = '17:00';
    }
}

// Show/hide end time based on attendance type (hide when Online)
export function handleAttendanceTypeChange() {
    const attendanceType = document.getElementById('attendanceType');
    const endTime = document.getElementById('endTime');
    if (!attendanceType || !endTime) return;
    const endGroup = endTime.closest('.form-group');
    const isOnline = (attendanceType.value || '').toLowerCase() === 'online';
    if (endGroup) endGroup.style.display = isOnline ? 'none' : '';
    if (isOnline) endTime.value = '';
}

export function handlePriorityChange() {
    const priority = document.getElementById('priority');
    const row = document.getElementById('justificationRow');
    if (!priority || !row) return;
    row.style.display = priority.value === 'Urgente' ? 'grid' : 'none';
}

// Mask and validate CPF
export function handleCpfMaskAndValidate(e) {
    const input = e.target;
    const digits = input.value.replace(/\D/g, '').slice(0, 11);
    let masked = '';
    if (digits.length > 0) masked = digits.slice(0, 3);
    if (digits.length > 3) masked += '.' + digits.slice(3, 6);
    if (digits.length > 6) masked += '.' + digits.slice(6, 9);
    if (digits.length > 9) masked += '-' + digits.slice(9, 11);
    input.value = masked;
    const isValid = validateCPF(digits);
    setFieldValidState(input, isValid, isValid ? '' : 'CPF inválido.');
}

// Allow only digits
export function allowOnlyDigits(e) { e.target.value = e.target.value.replace(/\D/g, ''); }

// Validate email format
export function validateEmailField(e) {
    const input = e.target;
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const ok = regex.test(input.value.trim());
    setFieldValidState(input, ok, ok ? '' : 'E-mail inválido.');
}

// Mark field/group as valid/invalid
export function setFieldValidState(input, valid, message) {
    const group = input.closest('.form-group');
    if (!group) return;
    const small = group.querySelector('.error-text');
    if (valid) { group.classList.remove('invalid'); if (small) small.textContent = ''; }
    else { group.classList.add('invalid'); if (small) small.textContent = message || 'Campo inválido'; }
}

// Submit handler with required fields
export function handleScheduleSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const requiredSelectors = ['#fullName','#serviceType'];
    let ok = true;
    requiredSelectors.forEach(sel => {
        const el = form.querySelector(sel);
        if (!el) return;
        const valid = Boolean(el.value && el.value.trim() !== '');
        setFieldValidState(el, valid, 'Campo obrigatório.');
        if (!valid) ok = false;
    });
    const cpfEl = document.getElementById('cpf');
    if (cpfEl && cpfEl.value) handleCpfMaskAndValidate({ target: cpfEl });
    if (!ok) { alert('Por favor, preencha os campos obrigatórios antes de continuar.'); return; }
    (async () => {
        try {
            const usuarioId = parseInt(localStorage.getItem('sga_usuario_id') || '1', 10);
            const nomeCompleto = form.querySelector('#fullName')?.value?.trim() || '';
            const cpf = (form.querySelector('#cpf')?.value || '').replace(/\D/g,'');
            const matricula = form.querySelector('#registration')?.value?.trim() || '';
            const cargo = form.querySelector('#role')?.value?.trim() || '';
            const tipoVinculo = form.querySelector('#bondType')?.value?.trim() || '';
            const localTrabalho = form.querySelector('#workplace')?.value?.trim() || '';
            const email = form.querySelector('#email')?.value?.trim() || '';
            const tipoServico = form.querySelector('#serviceType')?.value?.trim() || '';
            const prioridade = form.querySelector('#priority')?.value?.trim() || '';
            const tipoAtendimento = form.querySelector('#attendanceType')?.value?.trim() || '';
            const dataAgendamento = form.querySelector('#startDate')?.value?.trim() || '';
            const horaInicio = form.querySelector('#startTime')?.value?.trim() || '';
            let horaTermino = form.querySelector('#endTime')?.value?.trim() || '';
            const numeroProtocolo = form.querySelector('#protocol')?.value?.trim() || '';
            if (!horaTermino) {
                horaTermino = addMinutesToTime(horaInicio || '08:00', 30);
            }
            const payload = {
                usuario_id: usuarioId,
                nome_completo: nomeCompleto,
                cpf,
                matricula,
                cargo,
                tipo_vinculo: tipoVinculo,
                local_trabalho: localTrabalho,
                email,
                tipo_servico: tipoServico,
                prioridade,
                tipo_atendimento: tipoAtendimento,
                data_agendamento: dataAgendamento,
                hora_inicio: horaInicio || '08:00',
                hora_termino: horaTermino,
                numero_protocolo: numeroProtocolo || `TMP-${Date.now()}`
            };
            const resp = await apiAgendamentos.create(payload);
            alert('Agendamento realizado com sucesso!');
            const list = JSON.parse(localStorage.getItem('sas_protocol_history') || '[]');
            const proto = numeroProtocolo || '';
            if (proto) { list.push({ protocol: proto, createdAt: new Date().toISOString() }); localStorage.setItem('sas_protocol_history', JSON.stringify(list)); }
            form.reset();
            initSchedulePage();
        } catch (err) {
            alert(`Erro ao criar agendamento: ${err?.message || err}`);
        }
    })();
}

// Validate CPF digits
export function validateCPF(digits) {
    if (!digits || digits.length !== 11) return false;
    if (/^(\d)\1{10}$/.test(digits)) return false;
    const calc = (base) => { let sum = 0; for (let i = 0; i < base; i++) { sum += parseInt(digits[i], 10) * (base + 1 - i); } const mod = sum % 11; return (mod < 2) ? 0 : 11 - mod; };
    const d1 = calc(9); const d2 = calc(10);
    return d1 === parseInt(digits[9], 10) && d2 === parseInt(digits[10], 10);
}

export function addMinutesToTime(timeHHmm, minutesToAdd) {
    const [h, m] = timeHHmm.split(':').map(Number);
    const date = new Date();
    date.setHours(h, m, 0, 0);
    date.setMinutes(date.getMinutes() + minutesToAdd);
    const hh = String(date.getHours()).padStart(2, '0');
    const mm = String(date.getMinutes()).padStart(2, '0');
    return `${hh}:${mm}`;
}

// Persist schedule into localStorage
export function persistSchedule(form) {
    const data = {
        fullName: form.querySelector('#fullName')?.value || '',
        cpf: form.querySelector('#cpf')?.value || '',
        serviceType: form.querySelector('#serviceType')?.value || '',
        bondType: form.querySelector('#bondType')?.value || '',
        attendanceType: form.querySelector('#attendanceType')?.value || '',
        startDate: form.querySelector('#startDate')?.value || '',
        startTime: form.querySelector('#startTime')?.value || '',
        endTime: form.querySelector('#endTime')?.value || '',
        waitTime: form.querySelector('#waitTime')?.value || '',
        protocol: form.querySelector('#protocol')?.value || ''
    };
    const key = 'sas_schedules';
    const list = JSON.parse(localStorage.getItem(key) || '[]');
    list.push(data);
    localStorage.setItem(key, JSON.stringify(list));
}

// Export schedules to XLS (Excel-compatible)
export function exportSchedulesToXLS() {
    const key = 'sas_schedules';
    const list = JSON.parse(localStorage.getItem(key) || '[]');
    if (!list.length) { alert('Não há agendamentos para exportar.'); return; }
    const headers = [
        'Nome completo','CPF','Tipo de serviço','Tipo de vínculo','Tipo de atendimento',
        'Data do agendamento','Hora de início','Hora de término','Tempo de espera','Protocolo'
    ];
    const rows = list.map(item => [
        item.fullName || '', item.cpf || '', item.serviceType || '', item.bondType || '', item.attendanceType || '',
        item.startDate || '', item.startTime || '', item.endTime || '', item.waitTime || '', item.protocol || ''
    ]);
    const tableHtml = `
        <table border="1">
            <thead>
                <tr>${headers.map(h => `<th style="background:#E6EBF5;color:#0033A0;">${h}</th>`).join('')}</tr>
            </thead>
            <tbody>
                ${rows.map(r => `<tr>${r.map(c => `<td>${String(c).replace(/</g,'&lt;').replace(/>/g,'&gt;')}</td>`).join('')}</tr>`).join('')}
            </tbody>
        </table>`;
    const blob = new Blob([`\ufeff${tableHtml}`], { type: 'application/vnd.ms-excel;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agendamentos_${new Date().toISOString().slice(0,10)}.xls`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}


