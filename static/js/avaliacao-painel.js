/* Avaliação Painel Multinível */

const EIXO_LABELS = {
    "Governanca":              "Governança",
    "Politicas e Planos":      "Políticas e Planos",
    "Programas":               "Programas",
    "Linhas de Financiamento": "Linhas de Financiamento",
};

let eixoAtual         = "Governanca";
let estruturasData    = {};   // { setor: [estruturas] } or {}
let estruturaAtual    = "";

// ── Elementos ─────────────────────────────────────────────────
const tabs            = document.querySelectorAll(".ap-tabs li");
const setorGroup      = document.getElementById("ap-setor-group");
const setorLabel      = document.getElementById("ap-setor-label");
const setorSelect     = document.getElementById("ap-setor-select");
const estruturaLabel  = document.getElementById("ap-estrutura-label");
const estruturaSelect = document.getElementById("ap-estrutura-select");
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
    eixoLabel.textContent = EIXO_LABELS[eixo] || eixo;

    resetarTabela();
    carregarFiltros(eixo);
}

// ── Filtros ───────────────────────────────────────────────────
async function carregarFiltros(eixo) {
    setorGroup.style.display = "none";
    estruturaSelect.innerHTML = '<option value="">Selecione para mostrar a avaliação do item</option>';
    estruturaSelect.disabled  = true;
    estruturasData = {};

    try {
        const resp = await fetch(`/indicadores/api/avaliacao/filtros/?eixo=${encodeURIComponent(eixo)}`);
        const data = await resp.json();

        // Label da estrutura
        estruturaLabel.textContent = data.label_estrutura || "Estrutura";

        if (data.setores && data.setores.length > 0) {
            // Modo cascata: Setor → Estrutura
            estruturasData = data.estruturas_por_setor || {};
            setorLabel.textContent = data.label_setor || "Setor";

            setorSelect.innerHTML = '<option value="">Selecione o Setor</option>';
            data.setores.forEach((s) => {
                const opt = document.createElement("option");
                opt.value       = s;
                opt.textContent = s;
                setorSelect.appendChild(opt);
            });
            setorGroup.style.display = "flex";
        } else if (data.estruturas && data.estruturas.length > 0) {
            // Modo direto: só Estrutura
            preencherEstruturas(data.estruturas);
        }
    } catch (e) {
        console.error("Erro ao carregar filtros:", e);
        estruturaSelect.innerHTML = '<option value="">Não foi possível carregar os dados</option>';
        _setPlaceholderMsg("Falha ao conectar com o servidor. Verifique sua conexão e recarregue a página.", true);
        placeholder.style.display = "flex";
    }
}

function preencherEstruturas(lista) {
    estruturaSelect.innerHTML = '<option value="">Selecione para mostrar a avaliação do item</option>';
    lista.forEach((e) => {
        const opt = document.createElement("option");
        opt.value       = e;
        opt.textContent = e;
        estruturaSelect.appendChild(opt);
    });
    estruturaSelect.disabled = false;
}

// Cascata: Setor → Estrutura
setorSelect.addEventListener("change", () => {
    const setor = setorSelect.value;
    estruturaAtual = "";
    resetarTabela();

    if (!setor) {
        estruturaSelect.innerHTML = '<option value="">Selecione para mostrar a avaliação do item</option>';
        estruturaSelect.disabled  = true;
        return;
    }

    const lista = estruturasData[setor] || [];
    preencherEstruturas(lista);
});

// Seleção de Estrutura → carrega tabela
estruturaSelect.addEventListener("change", () => {
    estruturaAtual = estruturaSelect.value;
    if (!estruturaAtual) {
        resetarTabela();
        return;
    }
    carregarTabela(estruturaAtual);
});

// ── Tabela ────────────────────────────────────────────────────
async function carregarTabela(estrutura) {
    resetarTabela(true); // mostra loader

    try {
        const resp = await fetch(`/indicadores/api/avaliacao/tabela/?estrutura=${encodeURIComponent(estrutura)}`);
        const data = await resp.json();

        loader.style.display = "none";

        if (!data.rows || data.rows.length === 0) {
            _setPlaceholderMsg("Nenhum dado encontrado para esta estrutura.");
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
        _setPlaceholderMsg("Erro ao carregar dados. Verifique sua conexão e tente novamente.", true);
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
        _setPlaceholderMsg("Selecione um item para visualizar a avaliação.");
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
    const titulo  = modalTitle.textContent || "Ficha Técnica";
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
<html lang="pt-br">
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
<div class="print-footer">RADAR BRASIL &ndash; Impulsionando a Ação Climática Federativa</div>
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

        if (!data.campos || data.campos.length === 0) {
            modalBody.innerHTML = '<p style="color:#6a8fa0;font-style:italic;padding:20px;">Nenhuma informação disponível.</p>';
            return;
        }

        const frag = document.createDocumentFragment();
        data.campos.forEach((c) => {
            const div = document.createElement("div");
            div.className = "ap-ficha-campo";
            div.innerHTML = `
                <div class="ap-ficha-campo-label">${escHtml(c.label)}</div>
                <div class="ap-ficha-campo-valor">${escHtml(c.valor)}</div>
            `;
            frag.appendChild(div);
        });
        modalBody.appendChild(frag);

    } catch (e) {
        modalLoader.style.display = "none";
        modalBody.innerHTML = '<p style="color:#c00;padding:20px;">Erro ao carregar ficha técnica.</p>';
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
