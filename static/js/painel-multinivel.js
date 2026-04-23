const ABA_MAP = {
  "Governança":             "Governanca",
  "Políticas e Planos":     "Politicas e Planos",
  "Programas":              "Programas",
  "Linha de Financiamento": "Linhas de Financiamento",
};

let chartInstance = null;

function renderizarGrafico(dados) {
  const canvas = document.getElementById("pm-chart-governanca");
  const ctx    = canvas.getContext("2d");

  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels:   dados.labels,
      datasets: dados.datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label: function (context) {
              return ` ${context.dataset.label}: ${context.parsed.y} estruturas`;
            },
          },
        },
      },
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true, stepSize: 1 },
      },
    },
  });
}

async function carregarDados(nomeAba) {
  const eixo = ABA_MAP[nomeAba] || "Governanca";
  const url  = `/indicadores/api/painel-multinivel/?eixo=${encodeURIComponent(eixo)}`;

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
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const tabs     = document.querySelectorAll(".pm-tabs li");
  const abaNomes = ["Governança", "Políticas e Planos", "Programas", "Linha de Financiamento"];

  tabs.forEach((tab, idx) => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      carregarDados(abaNomes[idx]);
    });
  });

  carregarDados("Governança");
});