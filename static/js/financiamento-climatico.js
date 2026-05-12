/* Financiamento Climático – Radar Brasil */

const ROWS_PER_PAGE = 10;
let allRows = [];
let currentPage = 1;

// ── Utilitários ────────────────────────────────────────────────
function _qs(id) { return document.getElementById(id); }

function _getFilters() {
    return {
        programa:   _qs("fc-f-programa")?.value   || "",
        setor:      _qs("fc-f-setor")?.value      || "",
        modalidade: _qs("fc-f-modalidade")?.value  || "",
        origem:     _qs("fc-f-origem")?.value      || "",
        ente:       _qs("fc-f-ente")?.value        || "",
    };
}

function _buildQS(obj) {
    return Object.entries(obj)
        .filter(([, v]) => v)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
        .join("&");
}

function _showLoader(vis) {
    _qs("fc-loader")?.classList.toggle("hidden", !vis);
}

function _updateClearBtns() {
    document.querySelectorAll(".fc-select-clear").forEach(btn => {
        const target = _qs(btn.dataset.target);
        btn.classList.toggle("visible", !!(target && target.value));
    });
}

// ── Popula selects com opções do backend ──────────────────────
async function carregarFiltros() {
    try {
        const resp = await fetch("/indicadores/api/financiamento/filtros/");
        const data = await resp.json();

        _populateSelect("fc-f-programa",   data.programas   || [], "Todos");
        _populateSelect("fc-f-setor",      data.setores     || [], "Todos");
        _populateSelect("fc-f-modalidade", data.modalidades || [], "Todas");
        _populateSelect("fc-f-origem",     data.origens     || [], "Todas");
        _populateSelect("fc-f-ente",       data.entes       || [], "Todos");
    } catch (e) {
        console.error("Erro filtros:", e);
    }
}

function _populateSelect(id, items, placeholder) {
    const sel = _qs(id);
    if (!sel) return;
    sel.innerHTML = `<option value="">${placeholder}</option>`;
    items.forEach(v => {
        const opt = document.createElement("option");
        opt.value = v; opt.textContent = v;
        sel.appendChild(opt);
    });
}

// ── Carrega gráficos ──────────────────────────────────────────
async function carregarGraficos() {
    const qs = _buildQS(_getFilters());
    try {
        const resp = await fetch(`/indicadores/api/financiamento/graficos/${qs ? "?" + qs : ""}`);
        const data = await resp.json();
        renderChartSetor(data.setor  || {});
        renderChartOrigem(data.origem || {});
        renderChartEnte(data.ente    || {});
    } catch (e) {
        console.error("Erro gráficos:", e);
    }
}

function renderChartSetor(d) {
    const el = _qs("fc-chart-setor");
    if (!el || !d.labels || !d.labels.length) { if (el) el.innerHTML = _emptyMsg(); return; }

    // Ordena decrescente para mostrar maior à esquerda
    const paired = d.labels.map((l, i) => ({ l, v: d.values[i], t: (d.texts || [])[i] || "" }))
        .sort((a, b) => b.v - a.v);

    const trace = {
        type: "bar",
        x: paired.map(p => p.l),
        y: paired.map(p => p.v),
        text: paired.map(p => p.t),
        textposition: "outside",
        cliponaxis: false,
        hovertemplate: "<b>%{x}</b><br>%{text}<extra></extra>",
        marker: { color: "#2c7873" },
    };
    const layout = {
        margin: { l: 40, r: 20, t: 36, b: 80 },
        xaxis: {
            automargin: true,
            tickangle: -30,
            tickfont: { size: 10 },
        },
        yaxis: {
            showgrid: true,
            gridcolor: "#eef2f5",
            zeroline: false,
            showticklabels: false,
        },
        plot_bgcolor: "transparent",
        paper_bgcolor: "transparent",
        font: { family: "Roboto, sans-serif", size: 11 },
        showlegend: false,
    };
    Plotly.newPlot(el, [trace], layout, _config());
}

function renderChartOrigem(d) {
    const el = _qs("fc-chart-origem");
    if (!el || !d.labels || !d.labels.length) { if (el) el.innerHTML = _emptyMsg(); return; }

    const trace = {
        type: "pie",
        hole: 0.42,
        labels: d.labels,
        values: d.values,
        marker: {
            colors: d.colors && d.colors.length ? d.colors : [
                "#2c7873", "#1a3d4d", "#6fb3b8", "#f4a261", "#e76f51", "#52b788"
            ],
        },
        textinfo: "none",
        hovertemplate: "<b>%{label}</b><br>%{value} registros (%{percent})<extra></extra>",
    };
    const layout = {
        margin: { l: 10, r: 120, t: 10, b: 10 },
        plot_bgcolor: "transparent",
        paper_bgcolor: "transparent",
        font: { family: "Roboto, sans-serif", size: 11 },
        legend: {
            orientation: "v",
            x: 0.82, y: 0.5,
            xanchor: "left",
            yanchor: "middle",
            font: { size: 11 },
        },
    };
    Plotly.newPlot(el, [trace], layout, _config());
}

function renderChartEnte(d) {
    const el = _qs("fc-chart-ente");
    if (!el || !d.series || !d.series.length) { if (el) el.innerHTML = _emptyMsg(); return; }

    const colors = ["#2c7873", "#6fb3b8", "#f4a261", "#1a3d4d", "#52b788", "#e76f51"];
    const traces = d.series.map((s, i) => ({
        type: "bar",
        name: s.name,
        x: d.labels,
        y: s.values,
        text: s.values.map(v => v > 0 ? String(v) : ""),
        textposition: "outside",
        cliponaxis: false,
        marker: { color: s.color || colors[i % colors.length] },
        hovertemplate: "<b>%{x}</b><br>" + _esc(s.name) + ": %{y}<extra></extra>",
    }));
    const layout = {
        margin: { l: 40, r: 20, t: 36, b: 60 },
        barmode: "group",
        xaxis: { automargin: true, tickfont: { size: 11 } },
        yaxis: {
            showgrid: true,
            gridcolor: "#eef2f5",
            zeroline: false,
            showticklabels: false,
        },
        plot_bgcolor: "transparent",
        paper_bgcolor: "transparent",
        font: { family: "Roboto, sans-serif", size: 11 },
        legend: { orientation: "h", x: 0.5, xanchor: "center", y: -0.22 },
    };
    Plotly.newPlot(el, traces, layout, _config());
}

function _config() {
    return { displayModeBar: false, responsive: true };
}

function _emptyMsg() {
    return `<div style="text-align:center;color:#9bb;padding:30px 0;font-size:12px;">Sem dados</div>`;
}

// ── Carrega e renderiza tabela ─────────────────────────────────
async function carregarTabela() {
    _showLoader(true);
    const qs = _buildQS(_getFilters());
    try {
        const resp = await fetch(`/indicadores/api/financiamento/tabela/${qs ? "?" + qs : ""}`);
        const data = await resp.json();
        allRows = data.rows || [];
        currentPage = 1;
        renderTabela();
    } catch (e) {
        console.error("Erro tabela:", e);
    } finally {
        _showLoader(false);
    }
}

function renderTabela() {
    const tbody = _qs("fc-tbody");
    if (!tbody) return;

    const start = (currentPage - 1) * ROWS_PER_PAGE;
    const page  = allRows.slice(start, start + ROWS_PER_PAGE);

    if (!page.length) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;padding:24px;color:#9bb;">Nenhum dado encontrado.</td></tr>`;
        renderPaginacao();
        return;
    }

    tbody.innerHTML = page.map(r => `
        <tr>
          <td>${_esc(r.programa)}</td>
          <td>${_esc(r.setor)}</td>
          <td>${_esc(r.modalidade)}</td>
          <td>${_esc(r.origem)}</td>
          <td>${_esc(r.valor)}</td>
          <td>${_esc(r.contrapartida)}</td>
          <td class="fc-td-ente">${_esc(r.federal)}</td>
          <td>${_esc(r.estadual)}</td>
          <td>${_esc(r.municipal)}</td>
        </tr>`).join("");

    renderPaginacao();
}

function renderPaginacao() {
    const el = _qs("fc-pagination");
    if (!el) return;

    const total  = allRows.length;
    const pages  = Math.ceil(total / ROWS_PER_PAGE);
    const start  = (currentPage - 1) * ROWS_PER_PAGE + 1;
    const end    = Math.min(currentPage * ROWS_PER_PAGE, total);

    if (total === 0) { el.innerHTML = ""; return; }

    let html = `<span class="fc-page-info">${start}–${end} de ${total}</span>`;
    html += `<button class="fc-page-btn" id="fc-pg-prev" ${currentPage === 1 ? "disabled" : ""}>Anterior</button>`;

    const maxBtns = 5;
    let pStart = Math.max(1, currentPage - Math.floor(maxBtns / 2));
    let pEnd   = Math.min(pages, pStart + maxBtns - 1);
    if (pEnd - pStart < maxBtns - 1) pStart = Math.max(1, pEnd - maxBtns + 1);

    for (let p = pStart; p <= pEnd; p++) {
        html += `<button class="fc-page-btn ${p === currentPage ? "active" : ""}" data-page="${p}">${p}</button>`;
    }

    html += `<button class="fc-page-btn" id="fc-pg-next" ${currentPage === pages ? "disabled" : ""}>Próximo</button>`;
    el.innerHTML = html;

    _qs("fc-pg-prev")?.addEventListener("click", () => { if (currentPage > 1) { currentPage--; renderTabela(); } });
    _qs("fc-pg-next")?.addEventListener("click", () => { if (currentPage < pages) { currentPage++; renderTabela(); } });
    el.querySelectorAll(".fc-page-btn[data-page]").forEach(btn => {
        btn.addEventListener("click", () => { currentPage = parseInt(btn.dataset.page); renderTabela(); });
    });
}

function _esc(s) {
    if (!s) return "—";
    return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

// ── Aplica filtros (charts + tabela) ──────────────────────────
function aplicarFiltros() {
    _updateClearBtns();
    carregarGraficos();
    carregarTabela();
}

// ── Limpar filtros ────────────────────────────────────────────
function limparFiltros() {
    ["fc-f-programa", "fc-f-setor", "fc-f-modalidade", "fc-f-origem", "fc-f-ente"].forEach(id => {
        const el = _qs(id);
        if (el) el.value = "";
    });
    _updateClearBtns();
    aplicarFiltros();
}

// ── Exportar CSV ──────────────────────────────────────────────
function baixarDados() {
    if (!allRows.length) return;
    const headers = ["Programas e Linhas de Financiamento", "Setor", "Modalidade",
                     "Origem dos Recursos", "Valor do Financiamento", "Contrapartida",
                     "Repasse Federal", "Repasse Estadual", "Repasse Municipal"];
    const rows = allRows.map(r =>
        [r.programa, r.setor, r.modalidade, r.origem, r.valor,
         r.contrapartida, r.federal, r.estadual, r.municipal]
            .map(v => `"${String(v ?? "").replace(/"/g, '""')}"`).join(",")
    );
    const csv  = [headers.join(","), ...rows].join("\n");
    const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href = url; a.download = "radar-brasil-financiamento-climatico.csv";
    a.click();
    URL.revokeObjectURL(url);
}

// ── Bootstrap ──────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
    await carregarFiltros();
    aplicarFiltros();

    // Filtros
    ["fc-f-programa", "fc-f-setor", "fc-f-modalidade", "fc-f-origem", "fc-f-ente"].forEach(id => {
        _qs(id)?.addEventListener("change", aplicarFiltros);
    });

    // Botões X dos selects
    document.querySelectorAll(".fc-select-clear").forEach(btn => {
        btn.addEventListener("click", () => {
            const sel = _qs(btn.dataset.target);
            if (sel) { sel.value = ""; aplicarFiltros(); }
        });
    });

    _qs("fc-btn-limpar")?.addEventListener("click", limparFiltros);
    _qs("fc-btn-baixar")?.addEventListener("click", baixarDados);
    _qs("fc-btn-print")?.addEventListener("click", () => window.print());
});
