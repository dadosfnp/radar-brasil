const ctx = document.getElementById('pm-chart-governanca').getContext('2d');

// dados podem vir do backend via JSON renderizado no template ou via API
const dados = /* objeto vindo da sua base */;

new Chart(ctx, {
  type: 'horizontalBar', // ou 'bar' com indexAxis: 'y' nas versões novas
  data: {
    labels: dados.categorias,
    datasets: dados.series
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    // estilizar eixos, cores, etc. para ficar idêntico ao print
  }
});