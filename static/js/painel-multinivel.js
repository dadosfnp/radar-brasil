const ABA_MAP = {
  "Governança":             "Governanca",
  "Políticas e Planos":     "Politicas e Planos",
  "Programas":              "Programas",
  "Linha de Financiamento": "Linhas de Financiamento",
};

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

async function carregarDados(nomeAba) {
  const eixo = ABA_MAP[nomeAba] || "Governanca";
  const url  = `/indicadores/api/painel-multinivel/?eixo=${encodeURIComponent(eixo)}`;

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
  const tabs     = document.querySelectorAll(".pm-tabs li");
  const abaNomes = [
    "Governança",
    "Políticas e Planos",
    "Programas",
    "Linha de Financiamento",
  ];

  tabs.forEach((tab, idx) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      carregarDados(abaNomes[idx]);
    });
  });

  // Ativa aba via query param ?aba=0..3 (vindo da página inicial)
  const abaParam = new URLSearchParams(window.location.search).get("aba");
  const abaIdx   = abaParam !== null ? parseInt(abaParam, 10) : 0;
  const abaInicial = abaNomes[abaIdx] || "Governança";

  tabs.forEach((t) => t.classList.remove("active"));
  if (tabs[abaIdx]) tabs[abaIdx].classList.add("active");

  carregarDados(abaInicial);
});