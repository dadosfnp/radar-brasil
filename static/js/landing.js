/* Landing — mini-mapa mundi da hero, Brasil centralizado.
   Mesmo padrão de paleta/tooltip do Nível País (nota-pais.js), só que enxuto:
   sem filtros, sem pins, sem interação de zoom/arraste — só o hover no Brasil. */

const LP_GEOJSON_URL =
  "https://cdn.jsdelivr.net/gh/martynafford/natural-earth-geojson@master/110m/cultural/ne_110m_admin_0_countries.json";

// Única fonte da nota do Brasil no Nível País (não existe API — mesmo padrão de
// nota-pais.js: COUNTRY_NOTA). Mudar aqui também se o Nível País mudar de ano/nota.
const LP_BRASIL_NOTA_NUM = "3";
const LP_BRASIL_ANO = "2025";

// Badge "BRASIL 2025 / 3/5 / Nível País" — classes globais (.rb-brasil-badge-*, em
// base.css) reaproveitadas tal e qual em landing.js e nota-pais.js, pra garantir que
// os dois mapas mostrem a nota com o mesmo visual exato, sem duas copias divergirem
function construirBadgeBrasil(lang) {
  const titulo = lang === "en" ? "BRAZIL" : "BRASIL";
  const rotulo = { en: "Country Level", es: "Nivel País" }[lang] || "Nível País";
  return (
    `<span class="rb-brasil-badge-topo">${titulo} ${LP_BRASIL_ANO}</span>` +
    `<span class="rb-brasil-badge-nota">${LP_BRASIL_NOTA_NUM}<small>/5</small></span>` +
    `<span class="rb-brasil-badge-rotulo">${rotulo}</span>`
  );
}

function _lpGetIso(props) {
  return props.ISO_A3 || props.ADM0_A3 || props.iso_a3 || "";
}

function initLandingHeroMap() {
  const el = document.getElementById("lp-hero-map");
  if (!el || typeof L === "undefined") return;

  const lang = (document.documentElement.lang || "pt").slice(0, 2);

  const map = L.map(el, {
    // Centro deslocado a oeste pra empurrar o Brasil mais pro lado direito da tela,
    // longe da area do titulo/subtitulo (que fica no canto superior esquerdo)
    center: [-10, -62],
    zoom: 3,
    minZoom: 2,
    maxZoom: 3,
    zoomControl: false,
    dragging: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    boxZoom: false,
    keyboard: false,
    attributionControl: false,
    renderer: L.canvas({ padding: 0.5 }),
  });

  fetch(LP_GEOJSON_URL)
    .then((resp) => resp.json())
    .then((data) => {
      L.geoJSON(data, {
        style: (feature) => {
          const isBrazil = _lpGetIso(feature.properties) === "BRA";
          return {
            fillColor:   isBrazil ? "#264584" : "#B0BCC8",
            fillOpacity: isBrazil ? 0.92 : 0.55,
            color:       "#fff",
            weight:      0.6,
          };
        },
        onEachFeature: (feature, layer) => {
          if (_lpGetIso(feature.properties) !== "BRA") return;
          layer.bindTooltip(construirBadgeBrasil(lang), {
            sticky: true,
            className: "rb-brasil-badge",
            direction: "top",
            offset: [0, -4],
          });
          layer.on("mouseover", () => layer.setStyle({ fillOpacity: 1 }));
          layer.on("mouseout", () => layer.setStyle({ fillOpacity: 0.92 }));
        },
      }).addTo(map);
    })
    .catch((e) => console.error("Falha ao carregar o mapa da hero:", e));
}

// Pirâmide União/Estados/Municípios (_federalismo_triangle.html) começa com
// opacity:0 em metodologia.css e só aparece com a classe .meto-py-animate — em
// sobre.html isso é feito por um IntersectionObserver inline; landing.html inclui
// o mesmo partial mas não carrega aquele script, então a pirâmide ficava invisível
// pra sempre. Mesma lógica replicada aqui.
function initFederalismPyramid() {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const py = document.querySelector(".meto-pyramid-wrap");
  if (!py) return;
  if (reducedMotion) {
    py.classList.add("meto-py-animate");
    return;
  }
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          py.classList.add("meto-py-animate");
          observer.disconnect();
        }
      });
    },
    { threshold: 0.4 }
  );
  observer.observe(py);
}

document.addEventListener("DOMContentLoaded", () => {
  initLandingHeroMap();
  initFederalismPyramid();
});
