const EIXOS = [
  "Governanca",
  "Politicas e Planos",
  "Programas",
  "Linhas de Financiamento",
];

// Imagem de fundo do card-resumo de cada eixo (mesma imagem usada na Landing).
// URLs vêm resolvidas pelo Django em window.EIXO_IMAGENS (ver painel-multinivel.html)
// — nunca montar "/static/img/..." na mão aqui, quebra com o storage de manifest.
const EIXO_IMAGEM = window.EIXO_IMAGENS || {};

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

function _niveisOrdem(isEn) {
  return isEn
    ? ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]
    : ["Nível 1", "Nível 2", "Nível 3", "Nível 4", "Nível 5"];
}

// criterio → { nivel: count }, a partir de labels/datasets (mesmo shape do Chart.js)
function construirMatrizPorCriterio(dados) {
  const criterios = dados.labels;
  const matrix = {};
  criterios.forEach((c) => { matrix[c] = {}; });
  dados.datasets.forEach((ds) => {
    ds.data.forEach((val, i) => {
      if (val > 0) matrix[criterios[i]][ds.label] = val;
    });
  });
  return matrix;
}

// Barrinha de 5 segmentos coloridos até o nível médio (arredondado) do critério
function construirPillBar(nivelMedio, isEn) {
  const wrap = document.createElement("span");
  wrap.className = "pm-pill-bar";

  const arred = nivelMedio != null ? Math.max(0, Math.min(5, Math.round(nivelMedio))) : 0;
  const corNivel = arred > 0 ? NIVEL_COLORS[_niveisOrdem(isEn)[arred - 1]] : null;

  for (let i = 1; i <= 5; i++) {
    const seg = document.createElement("span");
    seg.className = "pm-pill-seg" + (i <= arred ? " filled" : "");
    if (i <= arred && corNivel) seg.style.background = corNivel;
    wrap.appendChild(seg);
  }

  const label = document.createElement("span");
  label.className = "pm-pill-label";
  label.textContent = (nivelMedio != null ? nivelMedio : "–") + "/5";
  wrap.appendChild(label);

  return wrap;
}

// Waffle detalhado (células + régua + legenda) de UM critério só
function construirWaffleCriterio(nomeCriterio, contagemPorNivel, isEn) {
  const container = document.createElement("div");
  container.className = "pm-waffle";

  const explicacao = document.createElement("p");
  explicacao.className = "pm-waffle-explicacao";
  explicacao.textContent = RBi18n.t(
    "Cada quadradinho representa um componente avaliado; a cor indica o nível (1 a 5) obtido por ele neste critério."
  );
  container.appendChild(explicacao);

  const niveisOrdem = _niveisOrdem(isEn);
  const total = niveisOrdem.reduce((acc, n) => acc + (contagemPorNivel[n] || 0), 0);

  const cells = document.createElement("div");
  cells.className = "pm-grid-cells";
  niveisOrdem.forEach((nivel) => {
    const count = contagemPorNivel[nivel] || 0;
    for (let i = 0; i < count; i++) {
      const cell = document.createElement("span");
      cell.className = "pm-grid-cell";
      cell.style.background = NIVEL_COLORS[nivel] || "#ccc";
      cell.style.borderColor = NIVEL_BORDER[nivel] || "#aaa";
      cell.title = `${nomeCriterio}: ${nivel}`;
      cells.appendChild(cell);
    }
  });
  container.appendChild(cells);

  if (total > 0) {
    const rulerCells = document.createElement("div");
    rulerCells.className = "pm-grid-cells pm-grid-ruler-cells";
    for (let i = 1; i <= total; i++) {
      const tick = document.createElement("span");
      if (i % 5 === 0) {
        tick.className = "pm-grid-cell pm-grid-tick pm-grid-tick--label";
        tick.textContent = String(i);
      } else {
        tick.className = "pm-grid-cell pm-grid-tick";
      }
      rulerCells.appendChild(tick);
    }
    container.appendChild(rulerCells);
  }

  const legend = document.createElement("div");
  legend.className = "pm-grid-legend";
  niveisOrdem.forEach((nivel) => {
    const item = document.createElement("span");
    item.className = "pm-grid-legend-item";
    const dot = document.createElement("span");
    dot.className = "pm-grid-legend-dot";
    dot.style.background = NIVEL_COLORS[nivel] || "#ccc";
    item.appendChild(dot);
    item.appendChild(document.createTextNode(nivel));
    legend.appendChild(item);
  });
  container.appendChild(legend);

  // Sincroniza scroll horizontal entre células e régua deste critério
  const rows = container.querySelectorAll(".pm-grid-cells");
  rows.forEach((el) => {
    el.addEventListener(
      "scroll",
      function () {
        const left = this.scrollLeft;
        rows.forEach((other) => { if (other !== this) other.scrollLeft = left; });
      },
      { passive: true }
    );
  });

  return container;
}

function construirCaret() {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "pm-criterio-caret");
  svg.setAttribute("width", "12");
  svg.setAttribute("height", "7");
  svg.setAttribute("viewBox", "0 0 10 6");
  svg.setAttribute("fill", "none");
  svg.setAttribute("aria-hidden", "true");
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", "M1 1l4 4 4-4");
  path.setAttribute("stroke", "currentColor");
  path.setAttribute("stroke-width", "1.6");
  path.setAttribute("stroke-linecap", "round");
  path.setAttribute("stroke-linejoin", "round");
  svg.appendChild(path);
  return svg;
}

// Resumo do eixo ativo (descrição + Nível Eixo + total de componentes), com a foto
// do eixo como fundo — mesma imagem usada nos cards de eixo da Landing
function construirResumoEixo(eixo, dados, isEn) {
  const resumo = document.createElement("div");
  resumo.className = "pm-eixo-resumo";
  const img = EIXO_IMAGEM[eixo];
  if (img) {
    resumo.style.backgroundImage =
      `linear-gradient(135deg, rgba(16,29,79,.88), rgba(16,29,79,.72)), url("${img}")`;
  }

  if (dados.descricao_eixo) {
    const desc = document.createElement("p");
    desc.className = "pm-eixo-descricao";
    desc.textContent = dados.descricao_eixo;
    resumo.appendChild(desc);
  }

  const meta = document.createElement("div");
  meta.className = "pm-eixo-meta";

  if (dados.nivel_eixo != null) {
    const score = document.createElement("span");
    score.className = "pm-eixo-score";
    const rotulo = isEn ? "Axis Level" : "Nível Eixo";
    score.textContent = rotulo + ": " + dados.nivel_eixo + "/5";
    meta.appendChild(score);
  }
  if (dados.total_componentes) {
    const total = document.createElement("span");
    total.className = "pm-eixo-total";
    const palavra = isEn ? "components evaluated" : "componentes avaliados";
    total.textContent = dados.total_componentes + " " + palavra;
    meta.appendChild(total);
  }
  resumo.appendChild(meta);

  return resumo;
}

// Lista de critérios em acordeão: cada um colapsado por padrão, com seta própria;
// vários podem ficar abertos ao mesmo tempo (só a troca de EIXO via abas é exclusiva)
function renderizarCriterios(eixo, dados) {
  const wrapper = document.getElementById("pm-chart-wrapper");
  if (!wrapper) return;
  wrapper.innerHTML = "";

  if (!dados.criterios || dados.criterios.length === 0) return;

  const isEn = (document.documentElement.lang || "").startsWith("en");
  const matrix = construirMatrizPorCriterio(dados);

  wrapper.appendChild(construirResumoEixo(eixo, dados, isEn));

  const lista = document.createElement("div");
  lista.className = "pm-criterios-lista";

  dados.criterios.forEach((criterio) => {
    const item = document.createElement("div");
    item.className = "pm-criterio-item";

    const header = document.createElement("button");
    header.type = "button";
    header.className = "pm-criterio-header";
    header.setAttribute("aria-expanded", "false");

    const info = document.createElement("span");
    info.className = "pm-criterio-info";

    const nomeRow = document.createElement("span");
    nomeRow.className = "pm-criterio-nome-row";
    const nome = document.createElement("span");
    nome.className = "pm-criterio-nome";
    nome.textContent = criterio.nome;
    nomeRow.appendChild(nome);
    if (criterio.peso > 1) {
      const peso = document.createElement("span");
      peso.className = "pm-criterio-peso";
      peso.textContent = (isEn ? "weight" : "peso") + " " + criterio.peso;
      nomeRow.appendChild(peso);
    }
    info.appendChild(nomeRow);

    if (criterio.descricao) {
      const desc = document.createElement("span");
      desc.className = "pm-criterio-desc";
      desc.textContent = criterio.descricao;
      info.appendChild(desc);
    }
    header.appendChild(info);

    const scoreWrap = document.createElement("span");
    scoreWrap.className = "pm-criterio-score";
    scoreWrap.appendChild(construirPillBar(criterio.nivel_medio, isEn));
    scoreWrap.appendChild(construirCaret());
    header.appendChild(scoreWrap);

    item.appendChild(header);

    const detalhe = document.createElement("div");
    detalhe.className = "pm-criterio-detalhe";
    detalhe.hidden = true;

    header.addEventListener("click", () => {
      const aberto = header.getAttribute("aria-expanded") === "true";
      const novoEstado = !aberto;
      header.setAttribute("aria-expanded", String(novoEstado));
      item.classList.toggle("open", novoEstado);
      if (novoEstado && !detalhe.dataset.built) {
        detalhe.appendChild(
          construirWaffleCriterio(criterio.nome, matrix[criterio.nome] || {}, isEn)
        );
        detalhe.dataset.built = "1";
      }
      detalhe.hidden = !novoEstado;
    });

    item.appendChild(detalhe);
    lista.appendChild(item);
  });

  wrapper.appendChild(lista);
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
    renderizarCriterios(eixo, dados);
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
