/* Financiamento Climático – Radar Brasil */

const ROWS_PER_PAGE = 10;
let allRows    = [];
let currentPage = 1;
let msInstances = {};   // { key: MultiSelect }

// ══════════════════════════════════════════════════════════════
// MultiSelect — dropdown com checkboxes
// ══════════════════════════════════════════════════════════════
class MultiSelect {
    // Registro global de todas as instâncias para garantir
    // que apenas um dropdown fique aberto por vez.
    static _all = [];

    constructor({ containerId, placeholder, onChange }) {
        this.el          = document.getElementById(containerId);
        this.placeholder = placeholder || RBi18n.t("Todos");
        this.onChange    = onChange;
        this.options     = [];
        this.selected    = new Set();   // vazio = "todos selecionados"
        this.isOpen      = false;
        this._fixedMode  = false;       // true quando usando position:fixed (mobile)
        this._openedAt   = 0;           // timestamp da última abertura (guarda scroll espúrio iOS)
        MultiSelect._all.push(this);
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
              <input type="text" placeholder="${RBi18n.t("Buscar...")}" autocomplete="off" spellcheck="false">
            </div>
            <div class="fc-ms-actions">
              <button type="button" class="fc-ms-action-btn js-select-all">${RBi18n.t("Todos")}</button>
              <button type="button" class="fc-ms-action-btn js-clear-all">${RBi18n.t("Nenhum")}</button>
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

        // Fecha ao clicar fora (desktop)
        document.addEventListener("click", e => {
            if (!this.el.contains(e.target) &&
                !this._dropdown.contains(e.target)) this._close();
        });

        // Fecha ao fazer scroll (evita dropdown "voando" na tela).
        // Guarda de 350 ms evita falso fechamento por scroll espúrio que o iOS Safari
        // dispara ao inserir um elemento position:fixed na tela.
        window.addEventListener("scroll", () => {
            if (this.isOpen && Date.now() - this._openedAt > 350) this._close();
        }, { passive: true });

        // Reposiciona ao redimensionar janela (portrait ↔ landscape)
        window.addEventListener("resize", () => { if (this.isOpen) this._close(); });
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
    _isMobile() { return window.innerWidth <= 768; }

    _toggle() { this.isOpen ? this._close() : this._open(); }

    _open() {
        // ── Fecha todos os outros antes de abrir este ──────────
        MultiSelect._all.forEach(ms => { if (ms !== this) ms._close(); });

        this._openedAt = Date.now();    // marca abertura para guard do scroll handler
        this.isOpen = true;
        this._dropdown.classList.add("open");
        this._trigger.classList.add("open");
        this.el.classList.add("is-open");
        this._searchEl.value = "";
        this._renderOptions();

        if (this._isMobile()) {
            this._openFixed();
        } else {
            this._smartPosition();
        }

        this._searchEl.focus();
    }

    _close() {
        if (!this.isOpen) return;
        this.isOpen = false;
        this._dropdown.classList.remove("open");
        this._trigger.classList.remove("open");
        this.el.classList.remove("is-open");
        this._dropdown.classList.remove("drop-up");

        // Limpa estilos inline aplicados pelo modo fixed (mobile)
        if (this._fixedMode) {
            const s = this._dropdown.style;
            s.position = s.width = s.left = s.top = s.bottom = s.maxHeight = "";
            this._fixedMode = false;
            MultiSelect._hideBackdrop();
        } else {
            this._dropdown.style.maxHeight = "";
        }
    }

    // ── Posicionamento mobile: position:fixed flutua acima de tudo ──
    _openFixed() {
        this._fixedMode = true;
        const r       = this._trigger.getBoundingClientRect();
        const vw      = window.innerWidth;
        const vh      = window.innerHeight;
        const w       = r.width;
        const left    = Math.min(r.left, vw - w - 4); // não sai pela direita
        const below   = vh - r.bottom - 8;
        const above   = r.top - 8;
        const maxH    = Math.min(260, Math.max(below, above, 180));

        const s = this._dropdown.style;
        s.position = "fixed";
        s.width    = w + "px";
        s.left     = left + "px";
        s.maxHeight= maxH + "px";
        s.zIndex   = "9999";

        if (below >= 180 || below >= above) {
            s.top    = (r.bottom + 3) + "px";
            s.bottom = "auto";
        } else {
            this._dropdown.classList.add("drop-up");
            s.top    = "auto";
            s.bottom = (vh - r.top + 3) + "px";
        }

        MultiSelect._showBackdrop(() => this._close());
    }

    // ── Posicionamento desktop: abre para cima se não houver espaço ──
    _smartPosition() {
        const DROPDOWN_MIN_H = 180;
        this._dropdown.classList.remove("drop-up");
        this._dropdown.style.maxHeight = "";

        const triggerRect = this._trigger.getBoundingClientRect();
        const spaceBelow  = window.innerHeight - triggerRect.bottom - 8;
        const spaceAbove  = triggerRect.top - 8;

        if (spaceBelow < DROPDOWN_MIN_H && spaceAbove > spaceBelow) {
            this._dropdown.classList.add("drop-up");
            this._dropdown.style.maxHeight = Math.min(260, spaceAbove) + "px";
        } else {
            this._dropdown.style.maxHeight = Math.min(260, spaceBelow) + "px";
        }
    }

    // ── Backdrop (mobile) ────────────────────────────────────
    static _showBackdrop(onClose) {
        let bd = document.getElementById("fc-ms-backdrop");
        if (!bd) {
            bd = document.createElement("div");
            bd.id = "fc-ms-backdrop";
            document.body.appendChild(bd);
        }
        bd.onclick = null;              // limpa handler anterior
        bd.style.cssText = `
            position:fixed;inset:0;z-index:9998;
            background:transparent;`;
        bd._handler = onClose;
        // Ativa o handler apenas no próximo frame para evitar que o "ghost click"
        // gerado pelo toque no trigger caia no backdrop e feche o dropdown.
        requestAnimationFrame(() => { bd.onclick = onClose; });
    }

    static _hideBackdrop() {
        const bd = document.getElementById("fc-ms-backdrop");
        if (bd) bd.style.cssText = "";
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
            this._optionsEl.innerHTML = `<div class="fc-ms-empty">${RBi18n.t("Nenhum resultado")}</div>`;
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
        this._countEl.textContent = sel === 0 ? `${tot} ${RBi18n.t("de")} ${tot}` : `${tot - sel} ${RBi18n.t("de")} ${tot}`;
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
                ? RBi18n.t("Nenhum selecionado")
                : `${shown} ${shown !== 1 ? RBi18n.t("selecionados") : RBi18n.t("selecionado")}`;
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

function _scrollToTabela() {
    const wrap = document.querySelector(".fc-table-wrap");
    if (!wrap) return;
    const top = wrap.getBoundingClientRect().top + window.scrollY - 16;
    window.scrollTo({ top, behavior: "smooth" });
}

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
    const t = RBi18n.t;
    const defs = [
        { key: "programa",   id: "ms-programa",   placeholder: t("Todos os Programas") },
        { key: "setor",      id: "ms-setor",      placeholder: t("Todos os Setores")   },
        { key: "modalidade", id: "ms-modalidade", placeholder: t("Todas as Modalidades") },
        { key: "origem",     id: "ms-origem",     placeholder: t("Todas as Origens")   },
        { key: "ente",       id: "ms-ente",       placeholder: t("Todos os Entes")     },
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
    const _chartIds = ["fc-chart-setor", "fc-chart-origem", "fc-chart-ente"];

    _chartIds.forEach(id => {
        const el = _qs(id);
        if (el) { el.style.transition = "opacity .18s"; el.style.opacity = "0.25"; }
    });

    try {
        const resp = await fetch(`/indicadores/api/financiamento/graficos/${qs ? "?" + qs : ""}`);
        const data = await resp.json();
        renderChartSetor(data.setor  || {});
        renderChartOrigem(data.origem || {});
        renderChartEnte(data.ente    || {});
    } catch (e) {
        console.error("Erro gráficos:", e);
    } finally {
        setTimeout(() => {
            _chartIds.forEach(id => {
                const el = _qs(id);
                if (el) el.style.opacity = "1";
            });
        }, 60);
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
            color: "#264584",
            line: { color: "#070e2a", width: 0.5 },
        },
    };
    Plotly.newPlot(el, [trace], {
        margin: { l: 30, r: 20, t: 30, b: 70 },
        xaxis: { tickangle: -35, tickfont: { size: 9 }, automargin: true },
        yaxis: { showgrid: true, gridcolor: "#eef2f5", zeroline: false, showticklabels: false },
        plot_bgcolor: "transparent", paper_bgcolor: "transparent",
        font: { family: "Roboto, sans-serif", size: 10 },
        showlegend: false,
        dragmode: false,
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

    const COLORS = ["#264584","#101d4f","#3b6cbf","#f4a261","#e76f51",
                    "#264584","#264584","#ffd166","#ef476f","#8aaad4"];
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
        hovertemplate: `<b>%{y}</b><br>%{x} ${RBi18n.t("registros")}<extra></extra>`,
        marker: { color: items.map(item => item.color) },
    }], {
        margin: { l: 170, r: 40, t: 4, b: 20 },
        xaxis: { showgrid: true, gridcolor: "#eef2f5", zeroline: false, tickfont: { size: 9 } },
        yaxis: { tickfont: { size: 9.5 }, automargin: false },
        plot_bgcolor: "transparent",
        paper_bgcolor: "transparent",
        font: { family: "Roboto, sans-serif", size: 10 },
        showlegend: false,
        dragmode: false,
    }, _plotConfig());
}

function renderChartEnte(d) {
    const el = _qs("fc-chart-ente");
    if (!el || !d.labels?.length) { if (el) el.innerHTML = _emptyMsg(); return; }

    const hasValues = d.values?.some(v => v > 0);
    if (!hasValues) { el.innerHTML = _emptyMsg(); return; }

    const COLORS = ["#264584", "#3b6cbf", "#f4a261"];
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
        dragmode: false,
    }, _plotConfig());
}

function _abbrevLabel(s, max) {
    return s && s.length > max ? s.slice(0, max - 1) + "…" : (s || "");
}

function _emptyMsg() {
    return `<div style="text-align:center;color:#9bb;padding:30px 0;font-size:12px;">${RBi18n.t("Sem dados")}</div>`;
}

function _plotConfig() { return { displayModeBar: false, responsive: true, scrollZoom: false }; }

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
            ${RBi18n.t("Nenhum dado encontrado.")}</td></tr>`;
        renderPaginacao();
        return;
    }

    tbody.innerHTML = page.map(r => `
        <tr>
          <td data-label="${RBi18n.t('Programa')}">${_esc(r.programa)}</td>
          <td data-label="${RBi18n.t('Setor')}">${_esc(r.setor)}</td>
          <td data-label="${RBi18n.t('Modalidade')}">${_esc(r.modalidade)}</td>
          <td data-label="${RBi18n.t('Origem')}">${_esc(r.origem)}</td>
          <td data-label="${RBi18n.t('Valor')}">${_esc(r.valor)}</td>
          <td data-label="${RBi18n.t('Contrapartida')}">${_esc(r.contrapartida)}</td>
          <td class="fc-td-ente" data-label="Federal">${_esc(r.federal)}</td>
          <td data-label="${RBi18n.t('Estadual')}">${_esc(r.estadual)}</td>
          <td data-label="${RBi18n.t('Municipal')}">${_esc(r.municipal)}</td>
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

    const t = RBi18n.t;
    let html = `<span class="fc-page-info">${start}–${end} ${t("de")} ${total}</span>`;
    html += `<button class="fc-page-btn" id="fc-pg-prev" ${currentPage === 1 ? "disabled" : ""}>${t("Anterior")}</button>`;

    const maxBtns = 5;
    let pStart = Math.max(1, currentPage - Math.floor(maxBtns / 2));
    const pEnd = Math.min(pages, pStart + maxBtns - 1);
    if (pEnd - pStart < maxBtns - 1) pStart = Math.max(1, pEnd - maxBtns + 1);

    for (let p = pStart; p <= pEnd; p++) {
        html += `<button class="fc-page-btn ${p === currentPage ? "active" : ""}" data-page="${p}">${p}</button>`;
    }

    html += `<button class="fc-page-btn" id="fc-pg-next" ${currentPage === pages ? "disabled" : ""}>${t("Próximo")}</button>`;
    el.innerHTML = html;

    _qs("fc-pg-prev")?.addEventListener("click", () => { if (currentPage > 1) { currentPage--; renderTabela(); _scrollToTabela(); } });
    _qs("fc-pg-next")?.addEventListener("click", () => { if (currentPage < pages) { currentPage++; renderTabela(); _scrollToTabela(); } });
    el.querySelectorAll(".fc-page-btn[data-page]").forEach(btn => {
        btn.addEventListener("click", () => { currentPage = parseInt(btn.dataset.page); renderTabela(); _scrollToTabela(); });
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
    const t = RBi18n.t;
    const headers = [t("Programas e Linhas de Financiamento"), t("Setor"), t("Modalidade"),
                     t("Origem dos Recursos"), t("Valor do Financiamento"), t("Contrapartida"),
                     t("Repasse Federal"), t("Repasse Estadual"), t("Repasse Municipal")];
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
