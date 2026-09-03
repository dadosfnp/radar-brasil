const EIXOS = [
  "Governanca",
  "Politicas e Planos",
  "Programas",
  "Linhas de Financiamento",
];

// Contagens de instâncias por eixo (para KPI dinâmico)
const EIXO_COUNTS = {
  "Governanca":              { count: 31, label_pt: "instâncias de governança", label_en: "governance instances" },
  "Politicas e Planos":     { count: 17, label_pt: "políticas e planos", label_en: "policies and plans" },
  "Programas":               { count: 18, label_pt: "programas", label_en: "programs" },
  "Linhas de Financiamento": { count: 17, label_pt: "linhas de financiamento", label_en: "financing lines" },
};

const NIVEL_COLORS = {
  "Nível 1":  "#e06b6b",
  "Nível 2":  "#f09a50",
  "Nível 3":  "#e8c53a",
  "Nível 4":  "#72be79",
  "Nível 5":  "#1a4a35",
  "Level 1":  "#e06b6b",
  "Level 2":  "#f09a50",
  "Level 3":  "#e8c53a",
  "Level 4":  "#72be79",
  "Level 5":  "#1a4a35",
};

const NIVEL_BORDER = {
  "Nível 1":  "#c85050",
  "Nível 2":  "#d87a30",
  "Nível 3":  "#c8a520",
  "Nível 4":  "#52a059",
  "Nível 5":  "#0f2d20",
  "Level 1":  "#c85050",
  "Level 2":  "#d87a30",
  "Level 3":  "#c8a520",
  "Level 4":  "#52a059",
  "Level 5":  "#0f2d20",
};

function renderizarGrid(dados) {
  const wrapper = document.getElementById("pm-chart-wrapper");
  if (!wrapper) return;

  wrapper.innerHTML = "";

  if (!dados.labels || dados.labels.length === 0) return;

  const isEn = (document.documentElement.lang || "").startsWith("en");
  const lang = isEn ? "en" : "pt";

  const criterios = dados.labels;
  const totalCriterios = criterios.length;

  // Monta mapa: criterio → { nivel: count }
  const matrix = {};
  criterios.forEach(c => { matrix[c] = {}; });
  dados.datasets.forEach(ds => {
    ds.data.forEach((val, i) => {
      if (val > 0) matrix[criterios[i]][ds.label] = val;
    });
  });

  // Calcula total de instâncias (soma de counts do primeiro critério)
  const firstCrit = criterios[0];
  const totalInstancias = Object.values(matrix[firstCrit] || {}).reduce((a, b) => a + b, 0);

  // Container principal
  const container = document.createElement("div");
  container.className = "pm-grid-container";

  // Para cada critério, renderiza uma linha de células
  criterios.forEach(criterio => {
    const row = document.createElement("div");
    row.className = "pm-grid-row";

    const rowLabel = document.createElement("div");
    rowLabel.className = "pm-grid-row-label";
    rowLabel.textContent = criterio;
    row.appendChild(rowLabel);

    const cells = document.createElement("div");
    cells.className = "pm-grid-cells";

    const niveisOrdem = isEn
      ? ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]
      : ["Nível 1", "Nível 2", "Nível 3", "Nível 4", "Nível 5"];

    niveisOrdem.forEach(nivel => {
      const count = matrix[criterio][nivel] || 0;
      for (let i = 0; i < count; i++) {
        const cell = document.createElement("span");
        cell.className = "pm-grid-cell";
        cell.style.background = NIVEL_COLORS[nivel] || "#ccc";
        cell.style.borderColor = NIVEL_BORDER[nivel] || "#aaa";
        cell.title = `${criterio}: ${nivel}`;
        cells.appendChild(cell);
      }
    });

    row.appendChild(cells);
    container.appendChild(row);
  });

  // Legenda
  const legend = document.createElement("div");
  legend.className = "pm-grid-legend";
  const niveisLegenda = isEn
    ? ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]
    : ["Nível 1", "Nível 2", "Nível 3", "Nível 4", "Nível 5"];

  niveisLegenda.forEach(nivel => {
    const item = document.createElement("span");
    item.className = "pm-grid-legend-item";
    const dot = document.createElement("span");
    dot.className = "pm-grid-legend-dot";
    dot.style.background = NIVEL_COLORS[nivel] || "#ccc";
    item.appendChild(dot);
    item.appendChild(document.createTextNode(nivel));
    legend.appendChild(item);
  });

  wrapper.appendChild(container);
  wrapper.appendChild(legend);
}

// Overlay de erro no gráfico
function _mostrarErroGrafico(msg) {
  const area = document.querySelector(".pm-chart-area");
  let err = area && area.querySelector(".pm-chart-error");
  if (!err) {
    err = document.createElement("div");
    err.className = "pm-chart-error";
    if (area) area.prepend(err);
  }
  err.textContent = msg;
  err.style.display = "flex";
  const wrapper = document.getElementById("pm-chart-wrapper");
  if (wrapper) wrapper.style.display = "none";
}

function _ocultarErroGrafico() {
  const err = document.querySelector(".pm-chart-area .pm-chart-error");
  if (err) err.style.display = "none";
  const wrapper = document.getElementById("pm-chart-wrapper");
  if (wrapper) wrapper.style.display = "";
}

function mostrarLoader(visivel) {
  const loader = document.getElementById("pm-loader");
  if (loader) loader.style.display = visivel ? "flex" : "none";
  const wrapper = document.getElementById("pm-chart-wrapper");
  if (wrapper) wrapper.style.opacity = visivel ? "0.3" : "1";
}

function atualizarKPI(eixo) {
  const info = EIXO_COUNTS[eixo];
  if (!info) return;
  const isEn = (document.documentElement.lang || "").startsWith("en");
  const valEl  = document.getElementById("pm-kpi-inst-value");
  const subEl  = document.getElementById("pm-kpi-inst-sub");
  if (valEl) valEl.textContent = info.count;
  if (subEl) subEl.textContent = isEn ? info.label_en : info.label_pt;
}

async function carregarDados(eixo) {
  const url = `/indicadores/api/painel-multinivel/?eixo=${encodeURIComponent(eixo)}`;
  _ocultarErroGrafico();
  mostrarLoader(true);
  try {
    const resp  = await fetch(url);
    const dados = await resp.json();
    if (dados.erro) {
      _mostrarErroGrafico("⚠ " + dados.erro);
      return;
    }
    _ocultarErroGrafico();
    renderizarGrid(dados);
  } catch (e) {
    console.error("Erro fetch:", e);
    _mostrarErroGrafico("⚠ " + RBi18n.t("Não foi possível carregar os dados. Verifique sua conexão e recarregue a página."));
  } finally {
    mostrarLoader(false);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".pm-tabs li");
  let abaIdxAtual = 0;

  function ativarAba(idx) {
    const tabpanel = document.getElementById("pm-chart-wrapper");
    tabs.forEach((t) => {
      t.classList.remove("active");
      const btn = t.querySelector("button");
      if (btn) btn.setAttribute("aria-selected", "false");
    });
    tabs[idx].classList.add("active");
    const activeBtn = tabs[idx].querySelector("button");
    if (activeBtn) {
      activeBtn.setAttribute("aria-selected", "true");
      if (tabpanel) tabpanel.setAttribute("aria-labelledby", activeBtn.id);
    }
    atualizarKPI(EIXOS[idx]);
  }

  tabs.forEach((tab, idx) => {
    tab.addEventListener("click", () => {
      abaIdxAtual = idx;
      ativarAba(idx);
      carregarDados(EIXOS[idx]);
    });

    const btn = tab.querySelector("button");
    if (btn) {
      btn.addEventListener("keydown", (e) => {
        let newIdx = idx;
        if      (e.key === "ArrowRight") { e.preventDefault(); newIdx = (idx + 1) % tabs.length; }
        else if (e.key === "ArrowLeft")  { e.preventDefault(); newIdx = (idx - 1 + tabs.length) % tabs.length; }
        else if (e.key === "Home")       { e.preventDefault(); newIdx = 0; }
        else if (e.key === "End")        { e.preventDefault(); newIdx = tabs.length - 1; }
        else return;
        abaIdxAtual = newIdx;
        ativarAba(newIdx);
        carregarDados(EIXOS[newIdx]);
        tabs[newIdx].querySelector("button")?.focus();
      });
    }
  });

  const abaParam = new URLSearchParams(window.location.search).get("aba");
  abaIdxAtual    = Math.max(0, Math.min(parseInt(abaParam, 10) || 0, EIXOS.length - 1));

  ativarAba(abaIdxAtual);
  carregarDados(EIXOS[abaIdxAtual]);

  const critBtn = document.querySelector(".pm-criteria-badge");
  if (critBtn) {
    critBtn.addEventListener("click", () => {
      window.location.href = `/indicadores/avaliacao-painel/?aba=${abaIdxAtual}`;
    });
  }
});
