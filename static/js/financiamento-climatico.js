/* Financiamento Climático – Radar Brasil */

const ROWS_PER_PAGE = 10;
let allRows    = [];
let currentPage = 1;
let msInstances = {};   // { key: MultiSelect }

// ══════════════════════════════════════════════════════════════
// MultiSelect — dropdown com checkboxes
// ══════════════════════════════════════════════════════════════
class MultiSelect {
    constructor({ containerId, placeholder, onChange }) {
        this.el          = document.getElementById(containerId);
        this.placeholder = placeholder || "Todos";
        this.onChange    = onChange;
        this.options     = [];
        this.selected    = new Set();   // vazio = "todos selecionados"
        this.isOpen      = false;
        this._build();
    }

    _build() {
        this.el.innerHTML = `
          <button type="button" class="fc-ms-trigger" aria-haspopup="listbox">
            <span class="fc-ms-trigger-label">${this.placeholder}</span>
            <svg class="fc-ms-arrow" width="10" height="6" viewBox="0 0 10 6" fill="none">
              <path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <div class="fc-ms-dropdown" role="listbox" aria-multiselectable="true">
            <div class="fc-ms-search">
              <input type="text" placeholder="Buscar..." autocomplete="off" spellcheck="false">
            </div>
            <div class="fc-ms-actions">
              <button type="button" class="fc-ms-action-btn js-select-all">Todos</button>
              <button type="button" class="fc-ms-action-btn js-clear-all">Nenhum</button>
              <span class="fc-ms-count-label"></span>
            </div>
            <div class="fc-ms-options"></div>
          </div>`;

        this._trigger    = this.el.querySelector(".fc-ms-trigger");
        this._dropdown   = this.el.querySelector(".fc-ms-dropdown");
        this._label      = this.el.querySelector(".fc-ms-trigger-label");
        this._optionsEl  = this.el.querySelector(".fc-ms-options");
        this._searchEl   = this.el.querySelector("input");
        this._countEl    = this.el.querySelector(".fc-ms-count-label");

        this._trigger.addEventListener("click", e => { e.stopPropagation(); this._toggle(); });
        this.el.querySelector(".js-select-all").addEventListener("click", () => this._selectAll());
        this.el.querySelector(".js-clear-all").addEventListener("click",  () => this._clearAll());
        this._searchEl.addEventListener("input", () => this._renderOptions(this._searchEl.value.toLowerCase()));

        document.addEventListener("click", e => {
            if (!this.el.contains(e.target)) this._close();
        });
    }

    // ── API pública ───────────────────────────────────────────
    setOptions(opts) {
        this.options  = opts;
        this.selected = new Set();
        this._renderOptions();
        this._updateLabel();
    }

    getSelected() { return [...this.selected]; }

    reset() {
        this.selected.clear();
        this._renderOptions();
        this._updateLabel();
    }

    // ── Internos ──────────────────────────────────────────────
    _toggle() { this.isOpen ? this._close() : this._open(); }

    _open() {
        this.isOpen = true;
        this._dropdown.classList.add("open");
        this._trigger.classList.add("open");
        this._searchEl.value = "";
        this._renderOptions();
        this._searchEl.focus();
    }

    _close() {
        this.isOpen = false;
        this._dropdown.classList.remove("open");
        this._trigger.classList.remove("open");
    }

    _selectAll() {
        this.selected.clear();                 // vazio = todos
        this._renderOptions(this._searchEl.value.toLowerCase());
        this._updateLabel();
        this.onChange([]);
    }

    _clearAll() {
        // "nenhum" = todos marcados como exclusão — usamos Set com todos para indicar "nenhum"
        // Tratamos: selected tem exatamente todos = "nenhum visível" → API filtra por lista vazia retorna 0
        this.options.forEach(o => this.selected.add(o));
        this._renderOptions(this._searchEl.value.toLowerCase());
        this._updateLabel();
        this.onChange(this.getSelected());
    }

    _toggle_option(val) {
        const allCount = this.options.length;

        if (this.selected.size === 0) {
            // Estava "todos" → agora remove este: seleciona todos os outros
            this.options.forEach(o => { if (o !== val) this.selected.add(o); });
        } else if (this.selected.has(val)) {
            this.selected.delete(val);
            if (this.selected.size === 0) {
                // Ficou vazio = "todos" novamente
            }
        } else {
            this.selected.add(val);
            if (this.selected.size === allCount) {
                this.selected.clear();  // todos marcados = "todos" = limpa
            }
        }

        this._renderOptions(this._searchEl.value.toLowerCase());
        this._updateLabel();
        this.onChange(this.getSelected());
    }

    _renderOptions(filter = "") {
        const visible = filter
            ? this.options.filter(o => o.toLowerCase().includes(filter))
            : this.options;

        if (!visible.length) {
            this._optionsEl.innerHTML = `<div class="fc-ms-empty">Nenhum resultado</div>`;
            return;
        }

        this._optionsEl.innerHTML = visible.map(opt => {
            // checked se selected está vazio (= todos) OU se este item está no set
            const checked = this.selected.size === 0 || this.selected.has(opt);
            const safeval = opt.replace(/"/g, "&quot;");
            return `
              <label class="fc-ms-option ${checked ? "is-checked" : ""}" data-val="${safeval}">
                <input type="checkbox" ${checked ? "checked" : ""}>
                <span>${opt}</span>
              </label>`;
        }).join("");

        this._optionsEl.querySelectorAll(".fc-ms-option").forEach(lbl => {
            lbl.addEventListener("click", e => {
                e.preventDefault();
                this._toggle_option(lbl.dataset.val);
            });
        });

        // Contagem
        const sel = this.selected.size;
        const tot = this.options.length;
        this._countEl.textContent = sel === 0 ? `${tot} de ${tot}` : `${tot - sel} de ${tot}`;
    }

    _updateLabel() {
        const n = this.selected.size;
        if (n === 0) {
            this._label.textContent = this.placeholder;
            this._label.classList.remove("has-selection");
            // Remove badge se existir
            this.el.querySelector(".fc-ms-badge")?.remove();
        } else {
            const excluded = n;
            const shown    = this.options.length - excluded;
            this._label.textContent = shown === 0
                ? "Nenhum selecionado"
                : `${shown} selecionado${shown !== 1 ? "s" : ""}`;
            this._label.classList.add("has-selection");

            let badge = this.el.querySelector(".fc-ms-badge");
            if (!badge) {
                badge = document.createElement("span");
                badge.className = "fc-ms-badge";
                this._trigger.insertBefore(badge, this.el.querySelector(".fc-ms-arrow"));
            }
            badge.textContent = shown;
        }
    }
}

// ══════════════════════════════════════════════════════════════
// Utilitários
// ══════════════════════════════════════════════════════════════
function _qs(id) { return document.getElementById(id); }

function _getFilters() {
    return {
        programa:   (msInstances.programa   || { getSelected: () => [] }).getSelected().join(","),
        setor:      (msInstances.setor      || { getSelected: () => [] }).getSelected().join(","),
        modalidade: (msInstances.modalidade || { getSelected: () => [] }).getSelected().join(","),
        origem:     (msInstances.origem     || { getSelected: () => [] }).getSelected().join(","),
        ente:       (msInstances.ente       || { getSelected: () => [] }).getSelected().join(","),
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

// ══════════════════════════════════════════════════════════════
// Inicialização dos MultiSelects
// ══════════════════════════════════════════════════════════════
function _initMultiSelects() {
    const defs = [
        { key: "programa",   id: "ms-programa",   placeholder: "Todos os Programas" },
        { key: "setor",      id: "ms-setor",      placeholder: "Todos os Setores"   },
        { key: "modalidade", id: "ms-modalidade", placeholder: "Todas as Modalidades" },
        { key: "origem",     id: "ms-origem",     placeholder: "Todas as Origens"   },
        { key: "ente",       id: "ms-ente",       placeholder: "Todos os Entes"     },
    ];
    defs.forEach(({ key, id, placeholder }) => {
        msInstances[key] = new MultiSelect({
            containerId: id,
            placeholder,
            onChange: () => aplicarFiltros(),
        });
    });
}

// ══════════════════════════════════════════════════════════════
// Carrega opções dos filtros
// ══════════════════════════════════════════════════════════════
async function carregarFiltros() {
    try {
        const resp = await fetch("/indicadores/api/financiamento/filtros/");
        const data = await resp.json();
        msInstances.programa?.setOptions(data.programas   || []);
        msInstances.setor?.setOptions(data.setores         || []);
        msInstances.modalidade?.setOptions(data.modalidades || []);
        msInstances.origem?.setOptions(data.origens        || []);
        msInstances.ente?.setOptions(data.entes            || []);
    } catch (e) {
        console.error("Erro filtros:", e);
    }
}

// ══════════════════════════════════════════════════════════════
// Gráficos
// ══════════════════════════════════════════════════════════════
let _origemData = null;

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
    if (!el || !d.labels?.length) { if (el) el.innerHTML = _emptyMsg(); return; }

    // Top 5 ordenados decrescente
    const paired = d.labels.map((l, i) => ({
        l, v: d.values[i], t: (d.texts || [])[i] || ""
    })).sort((a, b) => b.v - a.v).slice(0, 5);

    const trace = {
        type: "bar",
        x: paired.map(p => _abbrevLabel(p.l, 20)),
        y: paired.map(p => p.v),
        text: paired.map(p => p.t),
        textposition: "outside",
        cliponaxis: false,
        hovertext: paired.map(p => `<b>${p.l}</b><br>${p.t}`),
        hoverinfo: "text",
        marker: {
            color: "#2c7873",
            line: { color: "#1a5050", width: 0.5 },
        },
    };
    Plotly.newPlot(el, [trace], {
        margin: { l: 30, r: 20, t: 30, b: 70 },
        xaxis: { tickangle: -35, tickfont: { size: 9 }, automargin: true },
        yaxis: { showgrid: true, gridcolor: "#eef2f5", zeroline: false, showticklabels: false },
        plot_bgcolor: "transparent", paper_bgcolor: "transparent",
        font: { family: "Roboto, sans-serif", size: 10 },
        showlegend: false,
    }, _plotConfig());
}

function renderChartOrigem(d) {
    const el = _qs("fc-chart-origem");
    if (!el || !d.labels?.length) { if (el) el.innerHTML = _emptyMsg(); return; }
    _origemData = d;
    _drawOrigem();
}

function _drawOrigem() {
    const d  = _origemData;
    const el = _qs("fc-chart-origem");
    if (!el || !d) return;

    const COLORS = ["#2c7873","#1a3d4d","#6fb3b8","#f4a261","#e76f51",
                    "#52b788","#118ab2","#ffd166","#ef476f","#90e0ef"];
    const palette = d.colors?.length ? d.colors : COLORS;

    // Ordena ascendente para que o maior fique no topo (Plotly inverte eixo Y)
    const items = d.labels
        .map((l, i) => ({ label: l, value: d.values[i], color: palette[i % palette.length] }))
        .sort((a, b) => a.value - b.value);

    const BAR_H = 30;
    el.style.height = Math.max(60, items.length * BAR_H) + "px";

    Plotly.newPlot(el, [{
        type: "bar",
        orientation: "h",
        y: items.map(item => _abbrevLabel(item.label, 32)),
        x: items.map(item => item.value),
        text: items.map(item => String(item.value)),
        textposition: "inside",
        insidetextanchor: "middle",
        textfont: { color: "#fff", size: 9 },
        hovertemplate: "<b>%{y}</b><br>%{x} registros<extra></extra>",
        marker: { color: items.map(item => item.color) },
    }], {
        margin: { l: 170, r: 40, t: 4, b: 20 },
        xaxis: { showgrid: true, gridcolor: "#eef2f5", zeroline: false, tickfont: { size: 9 } },
        yaxis: { tickfont: { size: 9.5 }, automargin: false },
        plot_bgcolor: "transparent",
        paper_bgcolor: "transparent",
        font: { family: "Roboto, sans-serif", size: 10 },
        showlegend: false,
    }, _plotConfig());
}

function renderChartEnte(d) {
    const el = _qs("fc-chart-ente");
    if (!el || !d.labels?.length) { if (el) el.innerHTML = _emptyMsg(); return; }

    const hasValues = d.values?.some(v => v > 0);
    if (!hasValues) { el.innerHTML = _emptyMsg(); return; }

    const COLORS = ["#2c7873", "#6fb3b8", "#f4a261"];
    const texts  = d.texts || d.labels;

    Plotly.newPlot(el, [{
        type: "pie",
        hole: 0.44,
        labels: d.labels,
        values: d.values,
        customdata: texts,
        textinfo: "percent",
        hovertemplate: "<b>%{label}</b><br>%{customdata}<br>%{percent}<extra></extra>",
        domain: { x: [0.02, 0.62], y: [0.04, 0.96] },
        marker: { colors: COLORS.slice(0, d.labels.length) },
    }], {
        margin: { l: 4, r: 4, t: 10, b: 10 },
        plot_bgcolor: "transparent",
        paper_bgcolor: "transparent",
        font: { family: "Roboto, sans-serif", size: 10 },
        legend: {
            x: 0.66, y: 0.5, yanchor: "middle",
            font: { size: 10 },
            bgcolor: "transparent",
        },
        showlegend: true,
    }, _plotConfig());
}

function _abbrevLabel(s, max) {
    return s && s.length > max ? s.slice(0, max - 1) + "…" : (s || "");
}

function _emptyMsg() {
    return `<div style="text-align:center;color:#9bb;padding:30px 0;font-size:12px;">Sem dados</div>`;
}

function _plotConfig() { return { displayModeBar: false, responsive: true }; }

// ══════════════════════════════════════════════════════════════
// Tabela
// ══════════════════════════════════════════════════════════════
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
        tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;padding:24px;color:#9bb;">
            Nenhum dado encontrado.</td></tr>`;
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
    const el   = _qs("fc-pagination");
    if (!el) return;

    const total = allRows.length;
    const pages = Math.ceil(total / ROWS_PER_PAGE);
    const start = (currentPage - 1) * ROWS_PER_PAGE + 1;
    const end   = Math.min(currentPage * ROWS_PER_PAGE, total);

    if (total === 0) { el.innerHTML = ""; return; }

    let html = `<span class="fc-page-info">${start}–${end} de ${total}</span>`;
    html += `<button class="fc-page-btn" id="fc-pg-prev" ${currentPage === 1 ? "disabled" : ""}>Anterior</button>`;

    const maxBtns = 5;
    let pStart = Math.max(1, currentPage - Math.floor(maxBtns / 2));
    const pEnd = Math.min(pages, pStart + maxBtns - 1);
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
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ══════════════════════════════════════════════════════════════
// Filtrar / Limpar
// ══════════════════════════════════════════════════════════════
function aplicarFiltros() {
    carregarGraficos();
    carregarTabela();
}

function limparFiltros() {
    Object.values(msInstances).forEach(ms => ms.reset());
    aplicarFiltros();
}

// ══════════════════════════════════════════════════════════════
// Exportar CSV
// ══════════════════════════════════════════════════════════════
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

// ══════════════════════════════════════════════════════════════
// Bootstrap
// ══════════════════════════════════════════════════════════════
document.addEventListener("DOMContentLoaded", async () => {
    _initMultiSelects();
    await carregarFiltros();
    aplicarFiltros();

    _qs("fc-btn-limpar")?.addEventListener("click", limparFiltros);
    _qs("fc-btn-baixar")?.addEventListener("click", baixarDados);
    _qs("fc-btn-print")?.addEventListener("click", () => window.print());
});
