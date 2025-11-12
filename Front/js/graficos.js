// Gráficos page logic
// - Populate user filter
// - Render donut chart with tooltip

import { tryPopulateHeaderUser, initHeaderUserCommon, initReportsMenuClick } from './global.js';

document.addEventListener('DOMContentLoaded', function() {
    if (!window.location.pathname.includes('graficos.html')) return;
    initHeaderUserCommon();
    initReportsMenuClick();
    populateUsersInFilter();
    const btn = document.getElementById('btnGenerateChart');
    if (btn) btn.addEventListener('click', renderDonutChart);
});

export function populateUsersInFilter() {
    const sel = document.getElementById('userFilter');
    if (!sel) return;
    const users = new Set();
    const schedules = JSON.parse(localStorage.getItem('sas_schedules') || '[]');
    schedules.forEach(() => {
        const u = localStorage.getItem('sga_username');
        if (u) users.add(u);
    });
    users.forEach(u => { const opt = document.createElement('option'); opt.textContent = u; sel.appendChild(opt); });
}

export function renderDonutChart(canvasId = 'donutCanvas', tooltipId = 'chartTooltip') {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const data = [30, 15, 20, 10, 5, 20];
    const labels = ['Senha emitida', 'Chamada pela mesa', 'Atendimento iniciado', 'Encerrado', 'Não compareceu', 'Senha encerrada'];
    const colors = ['#0033A0', '#FFD100', '#009739', '#EF3340', '#6C757D', '#17A2B8'];
    const total = data.reduce((a,b)=>a+b,0);
    const cx = canvas.width/2;
    const cy = canvas.height/2;
    const outerR = Math.min(cx, cy) - 10;
    const innerR = outerR * 0.6;

    ctx.clearRect(0,0,canvas.width,canvas.height);
    let start = -Math.PI/2;
    const arcs = [];
    data.forEach((value, i) => {
        const angle = (value/total) * Math.PI * 2;
        const end = start + angle;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.fillStyle = colors[i % colors.length];
        ctx.arc(cx, cy, outerR, start, end);
        ctx.arc(cx, cy, innerR, end, start, true);
        ctx.closePath();
        ctx.fill();
        arcs.push({start, end, label: labels[i], value});
        start = end;
    });

    const tooltip = document.getElementById(tooltipId);
    canvas.onmousemove = function(e) {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const dx = x - cx;
        const dy = y - cy;
        const dist = Math.sqrt(dx*dx + dy*dy);
        const angle = Math.atan2(dy, dx);
        let theta = angle < -Math.PI/2 ? angle + Math.PI*2 : angle;
        theta += Math.PI/2; if (theta < 0) theta += Math.PI*2;
        const inside = dist <= outerR && dist >= innerR;
        if (inside) {
            const arc = arcs.find(a => theta >= a.start + Math.PI/2 && theta <= a.end + Math.PI/2);
            if (arc) {
                const pct = Math.round((arc.value/total)*100);
                tooltip.style.display = 'block';
                tooltip.style.left = `${e.pageX + 10}px`;
                tooltip.style.top = `${e.pageY + 10}px`;
                tooltip.textContent = `${arc.label}: ${arc.value} (${pct}%)`;
                return;
            }
        }
        tooltip.style.display = 'none';
    };
}


