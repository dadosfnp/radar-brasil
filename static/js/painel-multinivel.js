const EIXOS = [
  "Governanca",
  "Politicas e Planos",
  "Programas",
  "Linhas de Financiamento",
];

const NOME_EIXO = {
  "Governanca":              "Governança",
  "Politicas e Planos":      "Políticas e Planos",
  "Programas":               "Programas",
  "Linhas de Financiamento": "Linhas de Financiamento",
};

// Imagem de fundo do card de eixo recolhido (mesma imagem usada na Landing).
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

const cacheEixos = {};
let eixoAberto = null;

function _isEn() {
  return (document.documentElement.lang || "").startsWith("en");
}

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
    "Abaixo, cada célula corresponde a um componente avaliado neste critério, colorido pelo seu nível, numa escala de 1 a 5."
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

function construirCaret(direcao) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "pm-caret pm-caret--" + direcao);
  svg.setAttribute("width", "14");
  svg.setAttribute("height", "8");
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

async function fetchEixo(eixo) {
  if (cacheEixos[eixo]) return cacheEixos[eixo];
  const resp = await fetch(`/indicadores/api/painel-multinivel/?eixo=${encodeURIComponent(eixo)}`);
  const dados = await resp.json();
  cacheEixos[eixo] = dados;
  return dados;
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

// ── Visão geral: 4 eixos recolhidos, sem bolhas ──────────────────────────

function construirEixoOverviewCard(eixo, dados, isEn) {
  const card = document.createElement("button");
  card.type = "button";
  card.className = "pm-eixo-overview";
  const img = EIXO_IMAGEM[eixo];
  if (img) {
    card.style.backgroundImage =
      `linear-gradient(100deg, rgba(10,12,16,.62), rgba(10,12,16,.30)), url("${img}")`;
  }

  card.appendChild(construirCaret("down"));

  const info = document.createElement("span");
  info.className = "pm-eixo-overview-info";
  const nome = document.createElement("span");
  nome.className = "pm-eixo-overview-nome";
  nome.textContent = RBi18n.t(NOME_EIXO[eixo]);
  info.appendChild(nome);
  if (dados.descricao_eixo) {
    const desc = document.createElement("span");
    desc.className = "pm-eixo-overview-desc";
    desc.textContent = dados.descricao_eixo;
    info.appendChild(desc);
  }
  card.appendChild(info);

  const score = document.createElement("span");
  score.className = "pm-eixo-overview-score";
  const num = document.createElement("span");
  num.className = "pm-eixo-overview-score-num";
  num.appendChild(document.createTextNode(dados.nivel_eixo != null ? dados.nivel_eixo : "–"));
  const max = document.createElement("small");
  max.textContent = "/5";
  num.appendChild(max);
  score.appendChild(num);
  const label = document.createElement("span");
  label.className = "pm-eixo-overview-score-label";
  label.textContent = isEn ? "Axis Level" : "Nível Eixo";
  score.appendChild(label);
  card.appendChild(score);

  card.addEventListener("click", () => abrirEixo(eixo));
  return card;
}

async function renderVisaoGeral() {
  eixoAberto = null;
  renderPills(null); // bolhas continuam visiveis, so sem nenhuma marcada como ativa

  _ocultarErroGrafico();
  mostrarLoader(true);
  try {
    const isEn = _isEn();
    const todos = await Promise.all(EIXOS.map(fetchEixo));
    const wrapper = document.getElementById("pm-chart-wrapper");
    wrapper.innerHTML = "";
    const lista = document.createElement("div");
    lista.className = "pm-eixos-overview-list";
    EIXOS.forEach((eixo, i) => {
      lista.appendChild(construirEixoOverviewCard(eixo, todos[i], isEn));
    });
    wrapper.appendChild(lista);
  } catch (e) {
    console.error("Erro fetch:", e);
    _mostrarErroGrafico("⚠ " + RBi18n.t("Não foi possível carregar os dados. Verifique sua conexão e recarregue a página."));
  } finally {
    mostrarLoader(false);
  }
}

// ── Eixo expandido: bolhas + resumo + critérios em acordeão ──────────────

function construirResumoEixo(eixo, dados, isEn) {
  const resumo = document.createElement("div");
  resumo.className = "pm-eixo-resumo";

  const toggle = document.createElement("button");
  toggle.type = "button";
  toggle.className = "pm-eixo-resumo-toggle";
  toggle.setAttribute("aria-label", isEn ? "Back to overview" : "Voltar para a visão geral");
  toggle.appendChild(construirCaret("up"));
  toggle.addEventListener("click", renderVisaoGeral);
  resumo.appendChild(toggle);

  const titulo = document.createElement("span");
  titulo.className = "pm-eixo-resumo-titulo";
  const eyebrow = document.createElement("span");
  eyebrow.className = "pm-eixo-resumo-eyebrow";
  eyebrow.textContent = isEn ? "Axis" : "Eixo";
  titulo.appendChild(eyebrow);
  const nome = document.createElement("span");
  nome.className = "pm-eixo-resumo-nome";
  nome.textContent = RBi18n.t(NOME_EIXO[eixo]);
  titulo.appendChild(nome);
  resumo.appendChild(titulo);

  if (dados.descricao_eixo) {
    const desc = document.createElement("p");
    desc.className = "pm-eixo-resumo-descricao";
    desc.textContent = dados.descricao_eixo;
    resumo.appendChild(desc);
  }

  const meta = document.createElement("span");
  meta.className = "pm-eixo-resumo-meta";
  if (dados.total_componentes) {
    const total = document.createElement("span");
    total.className = "pm-eixo-resumo-total";
    total.textContent = dados.total_componentes + " " + (isEn ? "components evaluated" : "componentes avaliados");
    meta.appendChild(total);
  }
  const score = document.createElement("span");
  score.className = "pm-eixo-resumo-score";
  const num = document.createElement("span");
  num.className = "pm-eixo-resumo-score-num";
  num.appendChild(document.createTextNode(dados.nivel_eixo != null ? dados.nivel_eixo : "–"));
  const max = document.createElement("small");
  max.textContent = "/5";
  num.appendChild(max);
  score.appendChild(num);
  const scoreLabel = document.createElement("span");
  scoreLabel.className = "pm-eixo-resumo-score-label";
  scoreLabel.textContent = isEn ? "Axis Level" : "Nível Eixo";
  score.appendChild(scoreLabel);
  meta.appendChild(score);
  resumo.appendChild(meta);

  return resumo;
}

function renderizarCriterios(eixo, dados) {
  const wrapper = document.getElementById("pm-chart-wrapper");
  if (!wrapper) return;
  wrapper.innerHTML = "";

  const isEn = _isEn();

  // Retângulo cinza único que abraça o resumo do eixo + todos os seus critérios
  const expandido = document.createElement("div");
  expandido.className = "pm-eixo-expandido";
  expandido.appendChild(construirResumoEixo(eixo, dados, isEn));
  wrapper.appendChild(expandido);

  if (!dados.criterios || dados.criterios.length === 0) return;

  const matrix = construirMatrizPorCriterio(dados);
  const lista = document.createElement("div");
  lista.className = "pm-criterios-lista";

  dados.criterios.forEach((criterio) => {
    const item = document.createElement("div");
    item.className = "pm-criterio-item";

    const header = document.createElement("button");
    header.type = "button";
    header.className = "pm-criterio-header";
    header.setAttribute("aria-expanded", "false");
    header.appendChild(construirCaret("down"));

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

  expandido.appendChild(lista);
}

function renderPills(eixoAtivo) {
  const tabs = document.getElementById("pm-tabs");
  if (!tabs) return;
  tabs.querySelectorAll("button[data-eixo]").forEach((btn) => {
    const ativo = btn.dataset.eixo === eixoAtivo;
    btn.closest("li").classList.toggle("active", ativo);
    btn.setAttribute("aria-selected", String(ativo));
  });
}

async function abrirEixo(eixo) {
  eixoAberto = eixo;
  renderPills(eixo);

  _ocultarErroGrafico();
  mostrarLoader(true);
  try {
    const dados = await fetchEixo(eixo);
    if (dados.erro) {
      _mostrarErroGrafico("⚠ " + dados.erro);
      return;
    }
    renderizarCriterios(eixo, dados);
  } catch (e) {
    console.error("Erro fetch:", e);
    _mostrarErroGrafico("⚠ " + RBi18n.t("Não foi possível carregar os dados. Verifique sua conexão e recarregue a página."));
  } finally {
    mostrarLoader(false);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("#pm-tabs button[data-eixo]").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (btn.dataset.eixo !== eixoAberto) abrirEixo(btn.dataset.eixo);
    });
  });

  renderVisaoGeral();
});
