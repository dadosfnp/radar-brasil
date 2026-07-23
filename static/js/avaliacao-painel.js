/* Avaliação Painel Multinível */

/* ── Combobox ─────────────────────────────────────────────────
   Combobox customizado: busca por digitação, X para limpar,
   seta toggle, navegação por teclado, auto-fill bidirecional.
   ──────────────────────────────────────────────────────────── */
class Combobox {
    constructor(wrapId, { onSelect, onClear } = {}) {
        this.wrap     = document.getElementById(wrapId + "-wrap");
        this.input    = document.getElementById(wrapId + "-input");
        this.clearBtn = document.getElementById(wrapId + "-clear");
        this.toggle   = document.getElementById(wrapId + "-toggle");
        this.dropdown = document.getElementById(wrapId + "-dropdown");
        this.onSelect = onSelect || (() => {});
        this.onClear  = onClear  || (() => {});
        this._opts    = [];
        this._active  = -1;
        this._open    = false;
        this._bind();
    }

    setOptions(opts) {
        this._opts   = opts || [];
        this._active = -1;
        if (this._open) this._render(this.input.value);
    }

    setValue(val, silent = false) {
        this.input.value = val || "";
        this.clearBtn.style.display = val ? "flex" : "none";
        this._close();
        if (!silent && val) this.onSelect(val);
    }

    clear(silent = false) {
        this.input.value = "";
        this.clearBtn.style.display = "none";
        this._close();
        if (!silent) this.onClear();
    }

    _open_() {
        this._render(this.input.value);
        this.dropdown.hidden = false;
        this.wrap.dataset.open = "true";
        this.input.setAttribute("aria-expanded", "true");
        this._open = true;
    }

    _close() {
        this.dropdown.hidden = true;
        this.wrap.dataset.open = "false";
        this.input.setAttribute("aria-expanded", "false");
        this._active = -1;
        this._open = false;
    }

    _render(query) {
        const q = query.trim().toLowerCase();
        const filtered = q
            ? this._opts.filter(o => o.toLowerCase().includes(q))
            : this._opts;

        this.dropdown.innerHTML = "";
        this._active = -1;

        if (!filtered.length) {
            const li = document.createElement("li");
            li.className = "ap-combo-empty";
            li.textContent = RBi18n.t("Nenhum resultado encontrado");
            this.dropdown.appendChild(li);
            return;
        }

        filtered.forEach((opt) => {
            const li = document.createElement("li");
            li.className = "ap-combo-item";
            li.setAttribute("role", "option");
            li.dataset.value = opt;

            if (q) {
                const idx = opt.toLowerCase().indexOf(q);
                if (idx >= 0) {
                    li.appendChild(document.createTextNode(opt.slice(0, idx)));
                    const mark = document.createElement("mark");
                    mark.textContent = opt.slice(idx, idx + q.length);
                    li.appendChild(mark);
                    li.appendChild(document.createTextNode(opt.slice(idx + q.length)));
                } else {
                    li.textContent = opt;
                }
            } else {
                li.textContent = opt;
            }

            li.addEventListener("mousedown", (e) => {
                e.preventDefault();
                this._select(opt);
            });

            this.dropdown.appendChild(li);
        });
    }

    _select(val) {
        this.input.value = val;
        this.clearBtn.style.display = "flex";
        this._close();
        this.onSelect(val);
    }

    _moveActive(dir) {
        const items = this.dropdown.querySelectorAll(".ap-combo-item");
        if (!items.length) return;
        items[this._active]?.classList.remove("ap-combo-active");
        this._active = Math.max(0, Math.min(this._active + dir, items.length - 1));
        items[this._active].classList.add("ap-combo-active");
        items[this._active].scrollIntoView({ block: "nearest" });
    }

    _bind() {
        this.input.addEventListener("focus", () => {
            if (!this._open) this._open_();
        });

        this.input.addEventListener("input", () => {
            const val = this.input.value;
            this.clearBtn.style.display = val ? "flex" : "none";
            if (this._open) this._render(val);
            else this._open_();
        });

        this.input.addEventListener("keydown", (e) => {
            if (e.key === "ArrowDown") {
                e.preventDefault();
                if (!this._open) this._open_();
                else this._moveActive(1);
            } else if (e.key === "ArrowUp") {
                e.preventDefault();
                this._moveActive(-1);
            } else if (e.key === "Enter") {
                e.preventDefault();
                const active = this.dropdown.querySelector(".ap-combo-active");
                if (active) this._select(active.dataset.value);
                else this._close();
            } else if (e.key === "Escape" || e.key === "Tab") {
                this._close();
            }
        });

        this.input.addEventListener("blur", () => {
            setTimeout(() => { if (this._open) this._close(); }, 150);
        });

        this.toggle.addEventListener("mousedown", (e) => {
            e.preventDefault();
            if (this._open) { this._close(); }
            else { this.input.focus(); this._open_(); }
        });

        this.clearBtn.addEventListener("mousedown", (e) => {
            e.preventDefault();
            this.clear();
            this.input.focus();
        });
    }
}

const EIXO_LABELS = {
    "Governanca":              "Governança",
    "Politicas e Planos":      "Políticas e Planos",
    "Programas":               "Programas",
    "Linhas de Financiamento": "Linhas de Financiamento",
};
const EIXO_LABELS_EN = {
    "Governanca":              "Governance",
    "Politicas e Planos":      "Policies & Plans",
    "Programas":               "Programs",
    "Linhas de Financiamento": "Financing Lines",
};

let eixoAtual          = "Governanca";
let estruturaAtual     = "";
let todasEstruturas    = [];
let todosSetores       = [];
let estruturasPorSetor = {};
let setorPorEstrutura  = {};

// ── Elementos ─────────────────────────────────────────────────
const tabs           = document.querySelectorAll(".ap-tabs li");
const setorGroup     = document.getElementById("ap-setor-group");
const setorLabel     = document.getElementById("ap-setor-label");
const estruturaLabel = document.getElementById("ap-estrutura-label");

// Comboboxes
const comboEstrutura = new Combobox("ap-estrutura", {
    onSelect(val) {
        estruturaAtual = val;
        const setor = setorPorEstrutura[val];
        if (setor) comboSetor.setValue(setor, true);
        carregarTabela(val);
    },
    onClear() {
        estruturaAtual = "";
        comboSetor.clear(true);
        comboEstrutura.setOptions(todasEstruturas);
        resetarTabela();
    },
});

const comboSetor = new Combobox("ap-setor", {
    onSelect(setor) {
        const filtradas = estruturasPorSetor[setor] || [];
        comboEstrutura.setOptions(filtradas);
        if (filtradas.length === 1) {
            comboEstrutura.setValue(filtradas[0]);
        } else if (!filtradas.includes(estruturaAtual)) {
            comboEstrutura.clear(true);
            estruturaAtual = "";
            resetarTabela();
        }
    },
    onClear() {
        comboEstrutura.setOptions(todasEstruturas);
        if (estruturaAtual) {
            comboEstrutura.setValue(estruturaAtual, true);
        }
    },
});
const eixoLabel       = document.getElementById("ap-eixo-label");
const loader          = document.getElementById("ap-loader");
const placeholder     = document.getElementById("ap-placeholder");
const placeholderText = document.getElementById("ap-placeholder-text");
const tabela          = document.getElementById("ap-table");
const tabelaBody      = document.getElementById("ap-table-body");
const footerActions   = document.getElementById("ap-footer-actions");
const fichaBtn        = document.getElementById("ap-ficha-btn");
const modal           = document.getElementById("ap-modal");
const modalTitle      = document.getElementById("ap-modal-title");
const modalBody       = document.getElementById("ap-modal-body");
const modalClose      = document.getElementById("ap-modal-close");
const modalLoader     = document.getElementById("ap-modal-loader");
const linhaTempoBtn   = document.getElementById("ap-linha-tempo-btn");
const pdfBtn          = document.getElementById("ap-pdf-btn");

// ── Tabs ──────────────────────────────────────────────────────
const tabsArr = Array.from(tabs);

tabs.forEach((tab, idx) => {
    tab.addEventListener("click", () => {
        const eixo = tab.querySelector("button").dataset.eixo;
        ativarAba(eixo, tab);
    });

    const btn = tab.querySelector("button");
    if (btn) {
        btn.addEventListener("keydown", (e) => {
            let newIdx = idx;
            if      (e.key === "ArrowRight") { e.preventDefault(); newIdx = (idx + 1) % tabsArr.length; }
            else if (e.key === "ArrowLeft")  { e.preventDefault(); newIdx = (idx - 1 + tabsArr.length) % tabsArr.length; }
            else if (e.key === "Home")       { e.preventDefault(); newIdx = 0; }
            else if (e.key === "End")        { e.preventDefault(); newIdx = tabsArr.length - 1; }
            else return;
            const next    = tabsArr[newIdx];
            const nextBtn = next.querySelector("button");
            ativarAba(nextBtn.dataset.eixo, next);
            nextBtn.focus();
        });
    }
});

function ativarAba(eixo, tabEl) {
    tabs.forEach((t) => {
        t.classList.remove("active");
        const btn = t.querySelector("button");
        if (btn) btn.setAttribute("aria-selected", "false");
    });
    if (tabEl) {
        tabEl.classList.add("active");
        const btn = tabEl.querySelector("button");
        if (btn) {
            btn.setAttribute("aria-selected", "true");
            document.getElementById("ap-tabpanel").setAttribute("aria-labelledby", btn.id);
        }
    }

    eixoAtual      = eixo;
    estruturaAtual = "";
    eixoLabel.textContent  = RBi18n.getLang() === "en"
        ? (EIXO_LABELS_EN[eixo] || eixo)
        : (EIXO_LABELS[eixo] || eixo);

    resetarTabela();
    carregarFiltros(eixo);
}

// ── Filtros ───────────────────────────────────────────────────
async function carregarFiltros(eixo) {
    comboEstrutura.clear(true);
    comboSetor.clear(true);
    setorGroup.style.display = "none";
    todasEstruturas    = [];
    todosSetores       = [];
    estruturasPorSetor = {};
    setorPorEstrutura  = {};

    try {
        const resp = await fetch(`/indicadores/api/avaliacao/filtros/?eixo=${encodeURIComponent(eixo)}`);
        const data = await resp.json();

        estruturaLabel.textContent = RBi18n.t(data.label_estrutura || "Instância");
        setorLabel.textContent     = RBi18n.t(data.label_setor     || "Setor");

        todasEstruturas    = data.estruturas          || [];
        todosSetores       = data.setores             || [];
        estruturasPorSetor = data.estruturas_por_setor || {};
        setorPorEstrutura  = data.setor_por_estrutura  || {};

        comboEstrutura.setOptions(todasEstruturas);
        comboSetor.setOptions(todosSetores);

        if (todosSetores.length > 0) {
            setorGroup.style.display = "flex";
        }
    } catch (e) {
        console.error("Erro ao carregar filtros:", e);
        _setPlaceholderMsg(RBi18n.t("Falha ao conectar com o servidor. Verifique sua conexão e recarregue a página."), true);
        placeholder.style.display = "flex";
    }
}

// ── Tabela ────────────────────────────────────────────────────
async function carregarTabela(estrutura) {
    resetarTabela(true); // mostra loader

    try {
        const resp = await fetch(`/indicadores/api/avaliacao/tabela/?estrutura=${encodeURIComponent(estrutura)}`);
        const data = await resp.json();

        loader.style.display = "none";

        if (!data.rows || data.rows.length === 0) {
            _setPlaceholderMsg(RBi18n.t("Nenhum dado encontrado para esta estrutura."));
            placeholder.style.display = "flex";
            return;
        }

        tabelaBody.innerHTML = "";
        data.rows.forEach((row) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${escHtml(row.avaliacao)}</td>
                <td>${escHtml(row.criterio)}</td>
                <td style="text-align:center;">
                    <span class="ap-nivel-badge"
                          data-nivel="${escHtml(row.nivel)}"
                          style="background-color:${escHtml(row.cor)};">
                        ${escHtml(row.nivel)}
                    </span>
                </td>
            `;
            tabelaBody.appendChild(tr);
        });

        tabela.style.display = "table";
        footerActions.style.display = "flex";

    } catch (e) {
        loader.style.display = "none";
        _setPlaceholderMsg(RBi18n.t("Erro ao carregar dados. Verifique sua conexão e tente novamente."), true);
        placeholder.style.display = "flex";
        console.error("Erro tabela:", e);
    }
}

function _setPlaceholderMsg(msg, isError = false) {
    placeholder.className = isError ? "ap-placeholder ap-placeholder--error" : "ap-placeholder";
    if (placeholderText) placeholderText.textContent = msg;
    else placeholder.textContent = msg;
}

function resetarTabela(mostrarLoader = false) {
    tabela.style.display        = "none";
    footerActions.style.display = "none";
    tabelaBody.innerHTML        = "";

    if (mostrarLoader) {
        placeholder.style.display = "none";
        loader.style.display      = "flex";
    } else {
        loader.style.display      = "none";
        _setPlaceholderMsg(RBi18n.t("Selecione um item para visualizar a avaliação."));
        placeholder.style.display = "flex";
    }
}

// ── Modal Ficha Técnica ───────────────────────────────────────
const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

function abrirModal() {
    modal.style.display = "flex";
    const focusable = modal.querySelectorAll(FOCUSABLE);
    if (focusable.length) focusable[0].focus();
    document.addEventListener("keydown", trapFocus);
}

function fecharModal() {
    modal.style.display = "none";
    document.removeEventListener("keydown", trapFocus);
    fichaBtn.focus();
}

function trapFocus(e) {
    if (e.key === "Escape") { fecharModal(); return; }
    if (e.key !== "Tab") return;
    const focusable = Array.from(modal.querySelectorAll(FOCUSABLE)).filter(el => !el.closest('[style*="display: none"]') && !el.closest('[style*="display:none"]'));
    if (!focusable.length) return;
    const first = focusable[0];
    const last  = focusable[focusable.length - 1];
    if (e.shiftKey) {
        if (document.activeElement === first) { e.preventDefault(); last.focus(); }
    } else {
        if (document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
}

fichaBtn.addEventListener("click", () => abrirFicha(estruturaAtual));
modalClose.addEventListener("click", fecharModal);
modal.addEventListener("click", (e) => { if (e.target === modal) fecharModal(); });

pdfBtn.addEventListener("click", () => {
    const titulo  = modalTitle.textContent || RBi18n.t("Ficha Técnica");
    const campos  = modalBody.querySelectorAll(".ap-ficha-campo");
    if (!campos.length) return;

    let linhas = "";
    campos.forEach((c) => {
        const label = c.querySelector(".ap-ficha-campo-label")?.textContent || "";
        const valor = c.querySelector(".ap-ficha-campo-valor")?.textContent || "";
        linhas += `
            <div class="campo">
                <div class="campo-label">${escHtml(label)}</div>
                <div class="campo-valor">${escHtml(valor)}</div>
            </div>`;
    });

    const html = `<!DOCTYPE html>
<html lang="${RBi18n.getLang() === 'en' ? 'en-US' : 'pt-BR'}">
<head>
<meta charset="UTF-8">
<title>Ficha Técnica – ${escHtml(titulo)}</title>
<style>
  @page { margin: 20mm 18mm 28mm; }
  body { font-family: 'Roboto', Arial, sans-serif; margin: 0; padding: 12px 20px 48px;
         color: #1a3d4d; font-size: 13px; }
  h1   { font-size: 15px; font-weight: 700; color: #2c6174; text-transform: uppercase;
         letter-spacing: .06em; border-bottom: 2px solid #2c6174; padding-bottom: 8px; margin-bottom: 20px; }
  .campo { margin-bottom: 14px; padding-bottom: 14px; border-bottom: 1px solid #d4ece8; }
  .campo:last-child { border-bottom: none; }
  .campo-label { font-size: 10px; font-weight: 800; color: #0d2530; text-transform: uppercase;
                 letter-spacing: .07em; margin-bottom: 4px; }
  .campo-valor { font-size: 13px; color: #3a6070; line-height: 1.6; white-space: pre-wrap; }
  .print-footer { position: fixed; bottom: 0; left: 0; right: 0;
                  font-size: 9px; color: #2c6174; font-family: Arial, sans-serif;
                  padding: 6px 20px; border-top: 1px solid #d4ece8;
                  background: #fff; letter-spacing: .03em; }
</style>
</head>
<body>
<h1>${escHtml(titulo)}</h1>
${linhas}
<div class="print-footer">${RBi18n.t("RADAR BRASIL – Impulsionando a Ação Climática Federativa")}</div>
</body>
</html>`;

    const win = window.open("", "_blank", "width=800,height=900");
    win.document.write(html);
    win.document.close();
    win.focus();
    setTimeout(() => win.print(), 400);
});

async function abrirFicha(estrutura) {
    if (!estrutura) return;

    modalTitle.textContent = estrutura;
    modalBody.innerHTML    = "";
    modalBody.appendChild(modalLoader);
    modalLoader.style.display = "flex";
    abrirModal();

    linhaTempoBtn.href = `/indicadores/linha-do-tempo/?estrutura=${encodeURIComponent(estrutura)}`;

    try {
        const resp = await fetch(`/indicadores/api/avaliacao/ficha/?estrutura=${encodeURIComponent(estrutura)}`);
        const data = await resp.json();

        modalLoader.style.display = "none";

        // Título vira hiperlink quando a ficha tem Link_eixo
        if (data.link_eixo) {
            modalTitle.innerHTML = `<a href="${data.link_eixo}" target="_blank" rel="noopener noreferrer">${escHtml(estrutura)}</a>`;
        } else {
            modalTitle.textContent = estrutura;
        }

        if (!data.campos || data.campos.length === 0) {
            modalBody.innerHTML = `<p style="color:#6a8fa0;font-style:italic;padding:20px;">${RBi18n.t("Nenhuma informação disponível.")}</p>`;
            return;
        }

        const frag = document.createDocumentFragment();
        data.campos.forEach((c) => {
            const div = document.createElement("div");
            div.className = "ap-ficha-campo";
            const valorHtml = c.url
                ? `<a href="${c.url}" target="_blank" rel="noopener noreferrer">${escHtml(c.valor)}</a>`
                : escHtml(c.valor).replace(/\n/g, "<br>");
            div.innerHTML = `
                <div class="ap-ficha-campo-label">${escHtml(RBi18n.t(c.label))}</div>
                <div class="ap-ficha-campo-valor">${valorHtml}</div>
            `;
            frag.appendChild(div);
        });
        modalBody.appendChild(frag);

    } catch (e) {
        modalLoader.style.display = "none";
        modalBody.innerHTML = `<p style="color:#c00;padding:20px;">${RBi18n.t("Erro ao carregar ficha técnica.")}</p>`;
        console.error("Erro ficha:", e);
    }
}

// ── Utilitários ───────────────────────────────────────────────
function escHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

// ── Inicialização ─────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    // Lê ?aba= para ativar aba certa vindo do Painel Multinível
    const abaParam = new URLSearchParams(window.location.search).get("aba");
    const EIXOS    = ["Governanca", "Politicas e Planos", "Programas", "Linhas de Financiamento"];
    const abaIdx   = Math.max(0, Math.min(parseInt(abaParam, 10) || 0, EIXOS.length - 1));

    tabs.forEach((t) => t.classList.remove("active"));
    if (tabs[abaIdx]) tabs[abaIdx].classList.add("active");

    ativarAba(EIXOS[abaIdx], tabs[abaIdx]);
});
