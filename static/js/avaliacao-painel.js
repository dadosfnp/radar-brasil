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
const tabela          = document.getElementById("ap-table");
const tabelaBody      = document.getElementById("ap-table-body");
const footerActions   = document.getElementById("ap-footer-actions");
const fichaBtn        = document.getElementById("ap-ficha-btn");
const modal           = document.getElementById("ap-modal");
const modalTitle      = document.getElementById("ap-modal-title");
const modalBody       = document.getElementById("ap-modal-body");
const modalClose      = document.getElementById("ap-modal-close");
const modalLoader     = document.getElementById("ap-modal-loader");

// ── Tabs ──────────────────────────────────────────────────────
tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        const eixo = tab.querySelector("button").dataset.eixo;
        ativarAba(eixo, tab);
    });
});

function ativarAba(eixo, tabEl) {
    tabs.forEach((t) => t.classList.remove("active"));
    if (tabEl) tabEl.classList.add("active");

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
            placeholder.textContent = "Nenhum dado encontrado para esta estrutura.";
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
        placeholder.textContent = "Erro ao carregar dados.";
        placeholder.style.display = "flex";
        console.error("Erro tabela:", e);
    }
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
        placeholder.style.display = "flex";
        placeholder.textContent   = "Selecione um item para visualizar a avaliação.";
    }
}

// ── Modal Ficha Técnica ───────────────────────────────────────
fichaBtn.addEventListener("click", () => abrirFicha(estruturaAtual));
modalClose.addEventListener("click", () => { modal.style.display = "none"; });
modal.addEventListener("click", (e) => { if (e.target === modal) modal.style.display = "none"; });

async function abrirFicha(estrutura) {
    if (!estrutura) return;

    modalTitle.textContent = estrutura;
    modalBody.innerHTML    = "";
    modalBody.appendChild(modalLoader);
    modalLoader.style.display = "flex";
    modal.style.display = "flex";

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
