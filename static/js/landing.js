/* Landing — mini-mapa mundi da hero, Brasil centralizado.
   Mesmo padrão de paleta/tooltip do Nível País (nota-pais.js), só que enxuto:
   sem filtros, sem pins, sem interação de zoom/arraste — só o hover no Brasil. */

const LP_GEOJSON_URL =
  "https://cdn.jsdelivr.net/gh/martynafford/natural-earth-geojson@master/110m/cultural/ne_110m_admin_0_countries.json";

// Única fonte da nota do Brasil no Nível País (não existe API — mesmo padrão de
// nota-pais.js: COUNTRY_NOTA). Mudar aqui também se o Nível País mudar de ano/nota.
const LP_BRASIL_NOTA = "3/5";
const LP_BRASIL_ANO = "2025";

function _lpGetIso(props) {
  return props.ISO_A3 || props.ADM0_A3 || props.iso_a3 || "";
}

function initLandingHeroMap() {
  const el = document.getElementById("lp-hero-map");
  if (!el || typeof L === "undefined") return;

  const isEn = (document.documentElement.lang || "").startsWith("en");

  const map = L.map(el, {
    center: [-8, -48],
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
          const titulo = isEn ? "Brazil" : "Brasil";
          const rotulo = isEn ? "Country Level" : "Nível País";
          layer.bindTooltip(
            `<strong>${titulo} ${LP_BRASIL_ANO}</strong><br>${LP_BRASIL_NOTA} · ${rotulo}`,
            { sticky: true, className: "lp-map-tooltip lp-map-tooltip--brasil", direction: "top", offset: [0, -4] }
          );
          layer.on("mouseover", () => layer.setStyle({ fillOpacity: 1 }));
          layer.on("mouseout", () => layer.setStyle({ fillOpacity: 0.92 }));
        },
      }).addTo(map);
    })
    .catch((e) => console.error("Falha ao carregar o mapa da hero:", e));
}

document.addEventListener("DOMContentLoaded", initLandingHeroMap);
