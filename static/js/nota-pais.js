// ── NOTA PAÍS ─────────────────────────────────────────────────────

const GEOJSON_URL =
  "https://cdn.jsdelivr.net/gh/martynafford/natural-earth-geojson@master/110m/cultural/ne_110m_admin_0_countries.json";

const CONTINENT_COLORS = {
  "North America": "#3EC9D4",
  "South America": "#4AB88A",
  "Europe":        "#4E80C5",
  "Africa":        "#E8943A",
  "Asia":          "#EFC040",
  "Oceania":       "#9870C8",
  "Antarctica":    "#C0D0D8",
};

// Fallback continent by ISO_A3
const ISO_CONTINENT = {
  USA:"North America",CAN:"North America",MEX:"North America",
  GTM:"North America",BLZ:"North America",HND:"North America",
  SLV:"North America",NIC:"North America",CRI:"North America",PAN:"North America",
  CUB:"North America",JAM:"North America",HTI:"North America",DOM:"North America",
  BHS:"North America",TTO:"North America",BRB:"North America",
  VCT:"North America",GRD:"North America",ATG:"North America",
  KNA:"North America",LCA:"North America",DMA:"North America",
  COL:"South America",VEN:"South America",GUY:"South America",
  SUR:"South America",BRA:"South America",ECU:"South America",
  PER:"South America",BOL:"South America",PRY:"South America",
  CHL:"South America",ARG:"South America",URY:"South America",
  GBR:"Europe",FRA:"Europe",DEU:"Europe",ITA:"Europe",ESP:"Europe",
  PRT:"Europe",NLD:"Europe",BEL:"Europe",AUT:"Europe",CHE:"Europe",
  SWE:"Europe",NOR:"Europe",DNK:"Europe",FIN:"Europe",ISL:"Europe",
  IRL:"Europe",POL:"Europe",CZE:"Europe",SVK:"Europe",HUN:"Europe",
  ROU:"Europe",BGR:"Europe",GRC:"Europe",EST:"Europe",LVA:"Europe",
  LTU:"Europe",BLR:"Europe",UKR:"Europe",MDA:"Europe",HRV:"Europe",
  BIH:"Europe",SRB:"Europe",MNE:"Europe",MKD:"Europe",ALB:"Europe",
  SVN:"Europe",LUX:"Europe",MLT:"Europe",CYP:"Europe",RUS:"Europe",
  MAR:"Africa",DZA:"Africa",TUN:"Africa",LBY:"Africa",EGY:"Africa",
  MRT:"Africa",MLI:"Africa",NER:"Africa",TCD:"Africa",SDN:"Africa",
  ETH:"Africa",ERI:"Africa",DJI:"Africa",SOM:"Africa",KEN:"Africa",
  UGA:"Africa",TZA:"Africa",RWA:"Africa",BDI:"Africa",MOZ:"Africa",
  ZMB:"Africa",ZWE:"Africa",MWI:"Africa",AGO:"Africa",COD:"Africa",
  COG:"Africa",CAF:"Africa",CMR:"Africa",NGA:"Africa",GHA:"Africa",
  CIV:"Africa",LBR:"Africa",SLE:"Africa",GIN:"Africa",GNB:"Africa",
  SEN:"Africa",GMB:"Africa",CPV:"Africa",BFA:"Africa",TGO:"Africa",
  BEN:"Africa",GAB:"Africa",GNQ:"Africa",STP:"Africa",
  ZAF:"Africa",NAM:"Africa",BWA:"Africa",LSO:"Africa",SWZ:"Africa",
  MDG:"Africa",COM:"Africa",MUS:"Africa",SYC:"Africa",SSD:"Africa",
  TUR:"Asia",JOR:"Asia",LBN:"Asia",SYR:"Asia",IRQ:"Asia",
  SAU:"Asia",YEM:"Asia",OMN:"Asia",ARE:"Asia",QAT:"Asia",
  KWT:"Asia",BHR:"Asia",IRN:"Asia",AFG:"Asia",PAK:"Asia",
  IND:"Asia",NPL:"Asia",BTN:"Asia",BGD:"Asia",LKA:"Asia",MDV:"Asia",
  CHN:"Asia",MNG:"Asia",KOR:"Asia",PRK:"Asia",JPN:"Asia",
  THA:"Asia",VNM:"Asia",KHM:"Asia",LAO:"Asia",MMR:"Asia",
  MYS:"Asia",SGP:"Asia",BRN:"Asia",PHL:"Asia",IDN:"Asia",TLS:"Asia",
  KAZ:"Asia",UZB:"Asia",TKM:"Asia",KGZ:"Asia",TJK:"Asia",
  ARM:"Asia",AZE:"Asia",GEO:"Asia",ISR:"Asia",PSE:"Asia",
  AUS:"Oceania",NZL:"Oceania",PNG:"Oceania",FJI:"Oceania",
  SLB:"Oceania",VUT:"Oceania",WSM:"Oceania",TON:"Oceania",
  KIR:"Oceania",FSM:"Oceania",PLW:"Oceania",MHL:"Oceania",
  NRU:"Oceania",TUV:"Oceania",
  ATA:"Antarctica",
};

// Nomes dos países em português (usados nos labels do mapa e tooltips)
const NOMES_PT = {
  // Américas
  CAN:"Canadá", USA:"Estados Unidos da América", MEX:"México",
  GTM:"Guatemala", NIC:"Nicarágua", CRI:"Costa Rica", COL:"Colômbia",
  BHS:"Bahamas", JAM:"Jamaica", DOM:"República Dominicana", VCT:"São Vicente e Granadinas",
  BRA:"Brasil", BOL:"Bolívia", PRY:"Paraguai", CHL:"Chile",
  ARG:"Argentina", PER:"Peru", VEN:"Venezuela", ECU:"Equador",
  URY:"Uruguai", GUY:"Guiana", SUR:"Suriname", PAN:"Panamá",
  HND:"Honduras", SLV:"El Salvador", BLZ:"Belize", CUB:"Cuba",
  HTI:"Haiti", TTO:"Trinidad e Tobago",
  // Europa
  ISL:"Islândia", SWE:"Suécia", FIN:"Finlândia", DNK:"Dinamarca",
  GBR:"Reino Unido", NLD:"Países Baixos", BEL:"Bélgica", FRA:"França",
  PRT:"Portugal", ITA:"Itália", POL:"Polônia", EST:"Estônia", UKR:"Ucrânia",
  DEU:"Alemanha", ESP:"Espanha", NOR:"Noruega", IRL:"Irlanda", AUT:"Áustria",
  CHE:"Suíça", ROU:"Romênia", BGR:"Bulgária", GRC:"Grécia", HUN:"Hungria",
  CZE:"Tchéquia", SVK:"Eslováquia", HRV:"Croácia", SVN:"Eslovênia",
  LTU:"Lituânia", LVA:"Letônia", BLR:"Bielorrússia", MDA:"Moldávia",
  BIH:"Bósnia e Herzegovina", SRB:"Sérvia", MNE:"Montenegro",
  MKD:"Macedônia do Norte", ALB:"Albânia", RUS:"Rússia",
  // África
  MAR:"Marrocos", TUN:"Tunísia", DZA:"Argélia", LBY:"Líbia", EGY:"Egito",
  NGA:"Nigéria", GHA:"Gana", SLE:"Serra Leoa", TCD:"Chade", BFA:"Burkina Faso",
  CPV:"Cabo Verde", RWA:"Ruanda", KEN:"Quênia", ETH:"Etiópia",
  SYC:"Seicheles", SWZ:"Eswatini", LSO:"Lesoto",
  ZAF:"África do Sul", MOZ:"Moçambique", TZA:"Tanzânia", UGA:"Uganda",
  AGO:"Angola", ZMB:"Zâmbia", ZWE:"Zimbábue", NAM:"Namíbia",
  CMR:"Camarões", COD:"Congo (Rep. Dem.)", COG:"Congo", SDN:"Sudão",
  SOM:"Somália", MDG:"Madagáscar",
  // Ásia e Oriente Médio
  TUR:"Turquia", JOR:"Jordânia", ARE:"Emirados Árabes Unidos",
  TKM:"Turcomenistão", KGZ:"Quirguistão", MNG:"Mongólia",
  PAK:"Paquistão", BGD:"Bangladesh", BTN:"Butão",
  KOR:"Coreia do Sul", JPN:"Japão", PHL:"Filipinas",
  BRN:"Brunei", LKA:"Sri Lanka",
  CHN:"China", IND:"Índia", IRN:"Irã", IRQ:"Iraque",
  SAU:"Arábia Saudita", SYR:"Síria", AFG:"Afeganistão",
  KAZ:"Cazaquistão", UZB:"Uzbequistão", TJK:"Tadjiquistão",
  ARM:"Armênia", AZE:"Azerbaijão", GEO:"Geórgia",
  MYS:"Malásia", THA:"Tailândia", VNM:"Vietnã", IDN:"Indonésia",
  MMR:"Mianmar", KHM:"Camboja", LAO:"Laos", SGP:"Cingapura",
  // Oceania
  AUS:"Austrália", PLW:"Palau", PNG:"Papua Nova Guiné", KIR:"Kiribati",
  NZL:"Nova Zelândia", FJI:"Fiji",
};

// CHAMP Coalition signatories (ISO A3)
const CHAMP_SIGNATORIES = new Set([
  "CAN","USA","MEX","GTM","NIC","CRI","COL",
  "BHS","JAM","DOM","VCT",
  "BRA","BOL","PRY","CHL",
  "ISL","SWE","FIN","DNK","GBR","NLD","BEL","FRA","PRT","ITA","POL","EST","UKR",
  "MAR","TUN","JOR","ARE","TUR",
  "TKM","KGZ","MNG","PAK","BGD","BTN","KOR","JPN","PHL","BRN","LKA",
  "PLW","PNG","KIR","AUS",
  "RWA","KEN","ETH","NGA","GHA","SLE","TCD","BFA","CPV","SYC","SWZ","LSO",
]);

// Countries that score / have a Nota-País (only Brazil for now)
const COUNTRY_NOTA = {
  BRA: "Nível 3,0",
};

// Red pin SVG
const PIN_ICON = L.divIcon({
  className: "",
  html: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 24" width="12" height="18">
    <path d="M8 0C3.58 0 0 3.58 0 8c0 5.5 8 16 8 16s8-10.5 8-16C16 3.58 12.42 0 8 0z"
      fill="#E53935" stroke="#B71C1C" stroke-width="0.8"/>
    <circle cx="8" cy="8" r="3.2" fill="rgba(255,255,255,0.72)"/>
  </svg>`,
  iconSize: [12, 18],
  iconAnchor: [6, 18],
});

// Ocean labels
const OCEAN_LABELS = [
  { pos: [12, -140], text: "OCEANO PACÍFICO" },
  { pos: [-22, -26], text: "OCEANO ATLÂNTICO" },
  { pos: [-22,  78], text: "OCEANO ÍNDICO" },
];

const REGION_MAP = {
  "americas": ["North America", "South America"],
  "europe":   ["Europe"],
  "africa":   ["Africa"],
  "asia":     ["Asia"],
  "oceania":  ["Oceania"],
};

let map, geoLayer;
let currentRegion = "";
let pinMarkers = [];
let labelMarkers = [];

// ── REGION FILTER ─────────────────────────────────────────────────
function applyRegionFilter(region) {
  currentRegion = region;
  const allowed = region ? REGION_MAP[region] : null;

  if (geoLayer) {
    geoLayer.eachLayer(layer => {
      const continent = getContinent(layer.feature.properties);
      const match = !allowed || allowed.includes(continent);
      layer.setStyle({
        fillColor:   match ? (CONTINENT_COLORS[continent] || "#C0C8CC") : "#C0C8C8",
        fillOpacity: match ? 0.84 : 0.38,
        color: "#fff",
        weight: 0.7,
      });
    });
  }

  [...pinMarkers, ...labelMarkers].forEach(({ marker, continent }) => {
    const match = !allowed || allowed.includes(continent);
    if (match) {
      if (!map.hasLayer(marker)) marker.addTo(map);
    } else {
      if (map.hasLayer(marker)) map.removeLayer(marker);
    }
  });
}

// ── INIT ──────────────────────────────────────────────────────────
function init() {
  map = L.map("np-map", {
    center: [20, 15],
    zoom: 2,
    minZoom: 1,
    maxZoom: 6,
    zoomControl: true,
    attributionControl: true,
  });

  // Add ocean text labels
  OCEAN_LABELS.forEach(({ pos, text }) => {
    addTextMarker(pos, text, "np-ocean-label");
  });

  fetch(GEOJSON_URL)
    .then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then(buildMap)
    .catch(err => console.error("[Nota País] Erro ao carregar GeoJSON:", err));

  document.getElementById("np-f-regiao")
    ?.addEventListener("change", e => applyRegionFilter(e.target.value));

  document.getElementById("np-btn-limpar")
    ?.addEventListener("click", () => {
      ["np-f-pais","np-f-compromisso","np-f-iniciativa","np-f-regiao"]
        .forEach(id => { const el = document.getElementById(id); if (el) el.value = ""; });
      applyRegionFilter("");
    });

  document.getElementById("np-btn-print")
    ?.addEventListener("click", imprimirMapa);
}

// ── PRINT MAPA ───────────────────────────────────────────────────
async function imprimirMapa() {
  const btn = document.getElementById("np-btn-print");
  const mapContainer = document.querySelector(".np-map-container");
  if (!mapContainer) return;

  if (btn) { btn.disabled = true; btn.textContent = "Gerando…"; }

  try {
    const canvas = await html2canvas(mapContainer, {
      useCORS: true,
      allowTaint: true,
      scale: 2,
      backgroundColor: "#1a3a50",
    });
    const link = document.createElement("a");
    link.download = "radar-brasil-nota-pais.png";
    link.href = canvas.toDataURL("image/png");
    link.click();
  } catch (err) {
    console.error("Erro ao gerar imagem:", err);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg> Print Mapa`;
    }
  }
}

// ── HELPERS ──────────────────────────────────────────────────────
function brighten(hex, amount = 40) {
  const n = parseInt(hex.replace("#", ""), 16);
  const r = Math.min(255, (n >> 16) + amount);
  const g = Math.min(255, ((n >> 8) & 0xff) + amount);
  const b = Math.min(255, (n & 0xff) + amount);
  return "#" + [r, g, b].map(v => v.toString(16).padStart(2, "0")).join("");
}

function getIso(props) {
  const iso = props.ISO_A3 || props.ADM0_A3 || props.iso_a3 || "";
  return (iso === "-99" || iso === "") ? "" : iso;
}

function getName(props) {
  const iso = getIso(props);
  return NOMES_PT[iso] || props.NAME || props.ADMIN || props.name || "";
}

function getContinent(props) {
  const raw = props.CONTINENT || props.continent || "";
  if (raw && CONTINENT_COLORS[raw]) return raw;
  return ISO_CONTINENT[getIso(props)] || "Other";
}

function getCentroid(feature) {
  const geom = feature.geometry;
  if (!geom) return null;
  let ring = [];
  if (geom.type === "Polygon") {
    ring = geom.coordinates[0];
  } else if (geom.type === "MultiPolygon") {
    let maxLen = 0;
    geom.coordinates.forEach(poly => {
      if (poly[0].length > maxLen) { maxLen = poly[0].length; ring = poly[0]; }
    });
  }
  if (!ring.length) return null;
  let lat = 0, lng = 0;
  ring.forEach(c => { lng += c[0]; lat += c[1]; });
  return [lat / ring.length, lng / ring.length];
}

function addTextMarker(latlng, text, className) {
  const icon = L.divIcon({
    className: "",
    html: `<span class="leaflet-tooltip ${className}">${text}</span>`,
    iconSize: null,
    iconAnchor: null,
  });
  return L.marker(latlng, { icon, interactive: false, zIndexOffset: -2000 }).addTo(map);
}

// ── MAP BUILD ─────────────────────────────────────────────────────
function buildMap(data) {
  geoLayer = L.geoJSON(data, {
    style: feature => {
      const continent = getContinent(feature.properties);
      return {
        fillColor:   CONTINENT_COLORS[continent] || "#C0C8CC",
        fillOpacity: 0.84,
        color:       "#fff",
        weight:      0.7,
      };
    },
    onEachFeature: (feature, layer) => {
      const props = feature.properties;
      const iso   = getIso(props);
      const name  = getName(props);
      const nota  = COUNTRY_NOTA[iso];

      // Hover tooltip
      const tipClass = nota ? "np-tooltip np-tooltip-brazil" : "np-tooltip";
      const tipHtml  = nota
        ? `<strong>Nota</strong><br>${name}: ${nota}`
        : "Nota não atribuída";

      layer.bindTooltip(tipHtml, {
        sticky:    true,
        className: tipClass,
        direction: "top",
        offset:    [0, -6],
      });

      const continent = getContinent(props);
      layer.on({
        mouseover() {
          this.setStyle({ weight: 3.0, color: "#fff", fillOpacity: 1, fillColor: brighten(CONTINENT_COLORS[continent] || "#C0C8CC") });
          this.bringToFront();
        },
        mouseout() {
          const allowed = currentRegion ? REGION_MAP[currentRegion] : null;
          const match = !allowed || allowed.includes(continent);
          this.setStyle({
            fillColor:   match ? (CONTINENT_COLORS[continent] || "#C0C8CC") : "#C0C8C8",
            fillOpacity: match ? 0.84 : 0.38,
            color: "#fff",
            weight: 0.7,
          });
        },
      });
    },
  }).addTo(map);

  // Pin markers + country name labels (signatories)
  data.features.forEach(feature => {
    const iso = getIso(feature.properties);
    if (!iso || !CHAMP_SIGNATORIES.has(iso)) return;

    const centroid = getCentroid(feature);
    if (!centroid) return;

    const pin = L.marker(centroid, { icon: PIN_ICON, interactive: false, zIndexOffset: 500 }).addTo(map);
    const featureContinent = getContinent(feature.properties);
    pinMarkers.push({ marker: pin, continent: featureContinent });

    const name = getName(feature.properties);
    if (name) {
      const lbl = addTextMarker([centroid[0] - 1.8, centroid[1]], name, "np-country-label");
      labelMarkers.push({ marker: lbl, continent: featureContinent });
    }
  });

  // Country name labels (non-signatories)
  data.features.forEach(feature => {
    const iso = getIso(feature.properties);
    if (!iso || CHAMP_SIGNATORIES.has(iso)) return;

    const centroid = getCentroid(feature);
    if (!centroid) return;

    const name = getName(feature.properties);
    if (!name) return;

    const featureContinent = getContinent(feature.properties);
    const lbl = addTextMarker(centroid, name, "np-country-label np-country-label--minor");
    labelMarkers.push({ marker: lbl, continent: featureContinent });
  });
}

// ── BOOT ──────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", init);
