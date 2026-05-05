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

  chartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels:   dados.labels,
      datasets: dados.datasets,
    },
    options: {
      indexAxis: "y",                 // ← barras HORIZONTAIS
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 300 },   // animação rápida
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            usePointStyle: true,
            pointStyle: "rect",
            font: { size: 12 },
            padding: 16,
          },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const v = ctx.parsed.x;
              return ` ${ctx.dataset.label}: ${v} estrutura${v !== 1 ? "s" : ""}`;
            },
          },
        },
      },
      scales: {
        x: {
          stacked: true,
          beginAtZero: true,
          ticks: { stepSize: 1, precision: 0 },
          grid: { color: "rgba(0,0,0,0.06)" },
        },
        y: {
          stacked: true,
          ticks: {
            font: { size: 11 },
            // quebra labels longos em múltiplas linhas
            callback: function (value) {
              const label = this.getLabelForValue(value);
              const maxLen = 24;
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
            },
          },
        },
      },
    },
  });
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

  mostrarLoader(true);

  try {
    const resp  = await fetch(url);
    const dados = await resp.json();

    if (dados.erro) {
      console.error("Erro API:", dados.erro);
      return;
    }
    renderizarGrafico(dados);
  } catch (e) {
    console.error("Erro fetch:", e);
  } finally {
    mostrarLoader(false);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".pm-tabs li");

  tabs.forEach((tab, idx) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      carregarDados(EIXOS[idx]);
    });
  });

  // Ativa aba via query param ?aba=0..3 (vindo da página inicial)
  const abaParam = new URLSearchParams(window.location.search).get("aba");
  const abaIdx   = Math.max(0, Math.min(parseInt(abaParam, 10) || 0, EIXOS.length - 1));

  tabs.forEach((t) => t.classList.remove("active"));
  if (tabs[abaIdx]) tabs[abaIdx].classList.add("active");

  carregarDados(EIXOS[abaIdx]);
});