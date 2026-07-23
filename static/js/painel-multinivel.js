const EIXOS = [
  "Governanca",
  "Politicas e Planos",
  "Programas",
  "Linhas de Financiamento",
];

let chartInstance = null;

function renderizarGrafico(dados) {
  const canvas = document.getElementById("pm-chart-governanca");
  if (!canvas) return;

  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }

  if (!dados.labels || dados.labels.length === 0) {
    console.warn("Sem dados para renderizar.");
    return;
  }

  const ctx = canvas.getContext("2d");

  const barLabelsPlugin = {
    id: "barLabels",
    afterDatasetsDraw(chart) {
      const c = chart.ctx;
      chart.data.datasets.forEach((dataset, di) => {
        const meta = chart.getDatasetMeta(di);
        if (meta.hidden) return;
        meta.data.forEach((bar, i) => {
          const value = dataset.data[i];
          if (!value || value <= 0) return;
          const text    = dataset.label;
          const centerX = (bar.base + bar.x) / 2;
          const centerY = bar.y;
          c.save();
          c.font         = "600 10px Roboto, sans-serif";
          const bg = (dataset.backgroundColor || "").toLowerCase();
          c.fillStyle = bg === "#e8c53a" ? "rgba(55,35,0,.75)" : "rgba(255,255,255,.95)";
          c.textAlign    = "center";
          c.textBaseline = "middle";
          const segW = Math.abs(bar.x - bar.base);
          if (segW >= c.measureText(text).width + 6) {
            c.fillText(text, centerX, centerY);
          }
          c.restore();
        });
      });
    },
  };

  const isMobile = window.innerWidth < 600;
  const maxLen   = isMobile ? 15 : 24;
  const tickSize = isMobile ? 10 : 11;
  const yWidth   = isMobile ? 115 : 160;

  function wrapLabel(label) {
    if (label.length <= maxLen) return label;
    const words = label.split(" ");
    const lines = [];
    let line = "";
    words.forEach((w) => {
      if ((line + w).length > maxLen) {
        if (line) lines.push(line.trim());
        line = "";
      }
      line += w + " ";
    });
    if (line.trim()) lines.push(line.trim());
    return lines;
  }

  chartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels:   dados.labels,
      datasets: dados.datasets,
    },
    plugins: [barLabelsPlugin],
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 300 },
      layout: {
        padding: { left: isMobile ? 0 : 8, right: isMobile ? 4 : 8 },
      },
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            usePointStyle: true,
            pointStyle: "rect",
            font: { size: isMobile ? 10 : 12 },
            padding: isMobile ? 10 : 16,
            boxWidth: isMobile ? 10 : 14,
          },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const v = ctx.parsed.x;
              const label = v !== 1 ? RBi18n.t("estruturas") : RBi18n.t("estrutura");
              return ` ${ctx.dataset.label}: ${v} ${label}`;
            },
          },
        },
      },
      scales: {
        x: {
          stacked: true,
          beginAtZero: true,
          ticks: { stepSize: 1, precision: 0, font: { size: tickSize } },
          grid: { color: "rgba(0,0,0,0.06)" },
        },
        y: {
          stacked: true,
          afterFit(scale) {
            scale.width = Math.max(scale.width, yWidth);
          },
          ticks: {
            font: { size: tickSize },
            callback: function (value) {
              return wrapLabel(this.getLabelForValue(value));
            },
          },
        },
      },
    },
  });
}

// Overlay de erro no gráfico (não destrói o canvas)
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
}

function _ocultarErroGrafico() {
  const err = document.querySelector(".pm-chart-area .pm-chart-error");
  if (err) err.style.display = "none";
}

// Mostra spinner enquanto carrega
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
      console.error("Erro API:", dados.erro);
      _mostrarErroGrafico("⚠ " + dados.erro);
      return;
    }
    _ocultarErroGrafico();
    renderizarGrafico(dados);
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

  // Ativa aba via query param ?aba=0..3 (vindo da página inicial)
  const abaParam = new URLSearchParams(window.location.search).get("aba");
  abaIdxAtual    = Math.max(0, Math.min(parseInt(abaParam, 10) || 0, EIXOS.length - 1));

  ativarAba(abaIdxAtual);

  carregarDados(EIXOS[abaIdxAtual]);

  // Botão "Critérios e Parâmetros de Avaliação" → redireciona para a aba certa
  const critBtn = document.querySelector(".pm-criteria-badge");
  if (critBtn) {
    critBtn.addEventListener("click", () => {
      window.location.href = `/indicadores/avaliacao-painel/?aba=${abaIdxAtual}`;
    });
  }
});