// ── NOTA PAÍS ─────────────────────────────────────────────────────

const GEOJSON_URL =
  "https://cdn.jsdelivr.net/gh/martynafford/natural-earth-geojson@master/110m/cultural/ne_110m_admin_0_countries.json";

const CONTINENT_COLORS = {
  "North America": "#161C4E",
  "South America": "#161C4E",
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

// Posições corretas dos labels — substitui o centróide calculado para países
// com geometria problemática (territórios ultramarinos, ilhas, países muito pequenos)
const LABEL_OVERRIDES = {
  // ── Europa ──
  FRA: [46.5,  2.5],   // exclui Guiana Francesa / outros territórios
  GBR: [53.5, -1.5],   // foco na ilha principal
  NOR: [64.5, 14.5],   // evita Svalbard e ilhas do Ártico
  ISL: [64.9,-18.5],
  SWE: [60.1, 15.0],
  FIN: [63.5, 25.5],
  DNK: [56.0, 10.0],   // exclui Groenlândia
  IRL: [53.2, -8.0],
  NLD: [52.3,  5.3],
  BEL: [50.5,  4.3],
  LUX: [49.8,  6.1],
  DEU: [51.0, 10.0],
  POL: [52.0, 19.5],
  CZE: [49.8, 15.5],
  SVK: [48.7, 19.5],
  AUT: [47.5, 13.5],
  CHE: [46.8,  8.3],
  SVN: [46.1, 14.8],
  HRV: [45.4, 16.5],
  BIH: [44.2, 17.5],
  SRB: [44.0, 21.0],
  MNE: [42.8, 19.4],
  MKD: [41.6, 21.7],
  ALB: [41.2, 20.2],
  HUN: [47.0, 19.5],
  ROU: [45.9, 24.9],
  BGR: [42.7, 25.5],
  GRC: [39.5, 22.5],
  MDA: [47.1, 28.4],
  EST: [58.7, 25.0],
  LVA: [57.0, 24.9],
  LTU: [55.7, 23.9],
  BLR: [53.7, 27.8],
  UKR: [49.0, 32.0],
  PRT: [39.7, -8.0],
  ESP: [40.2, -3.7],
  ITA: [42.8, 12.6],
  RUS: [61.5, 90.0],   // centro real da Rússia; não Europa
  // ── Américas ──
  USA: [38.0,-97.0],
  CAN: [56.0,-96.0],
  MEX: [23.5,-102.5],
  BRA: [-14.0,-51.9],
  CHL: [-35.0,-71.5],  // país muito comprido
  ARG: [-38.0,-65.0],
  COL: [  4.5,-74.0],
  BOL: [-16.5,-64.5],
  PRY: [-23.4,-58.4],
  URY: [-32.5,-56.0],
  PER: [-10.0,-75.0],
  ECU: [ -1.8,-78.2],
  VEN: [  8.0,-66.0],
  GUY: [  4.8,-58.9],
  SUR: [  4.0,-56.0],
  GTM: [ 15.8,-90.3],
  NIC: [ 12.9,-85.2],
  CRI: [  9.7,-84.0],
  PAN: [  8.5,-80.0],
  // Caribe (ilhas pequenas)
  BHS: [ 25.0,-77.5],
  JAM: [ 18.1,-77.3],
  DOM: [ 18.9,-70.2],
  VCT: [ 13.2,-61.2],
  TTO: [ 10.7,-61.2],
  CUB: [ 22.0,-79.5],
  HTI: [ 19.0,-72.5],
  // ── Ásia ──
  TUR: [ 39.0, 35.0],
  IRN: [ 32.0, 53.0],
  IRQ: [ 33.0, 44.0],
  SAU: [ 24.0, 45.0],
  JOR: [ 31.3, 36.5],
  ARE: [ 24.0, 54.0],
  CHN: [ 35.0,103.0],
  MNG: [ 46.5,103.0],
  KAZ: [ 48.0, 67.0],
  UZB: [ 41.5, 63.5],
  TKM: [ 39.0, 59.0],
  TJK: [ 38.9, 71.0],
  KGZ: [ 41.2, 74.5],
  AFG: [ 33.5, 65.0],
  PAK: [ 30.0, 69.0],
  IND: [ 22.0, 79.0],
  BGD: [ 24.0, 90.0],
  BTN: [ 27.5, 90.5],
  NPL: [ 28.2, 83.9],
  LKA: [  7.9, 80.7],
  MMR: [ 19.0, 96.5],
  THA: [ 15.0,101.0],
  VNM: [ 16.0,107.0],
  KHM: [ 12.5,104.9],
  LAO: [ 18.2,103.9],
  JPN: [ 36.5,138.0],
  KOR: [ 36.5,128.0],
  PHL: [ 12.5,123.0],  // arquipélago
  MYS: [  4.0,109.5],  // dividido Malásia peninsular + Bornéu
  IDN: [ -2.5,118.0],  // arquipélago extenso
  BRN: [  4.5,114.7],
  SGP: [  1.4,103.8],
  ARM: [ 40.1, 45.0],
  AZE: [ 40.3, 47.5],
  GEO: [ 42.0, 43.5],
  ISR: [ 31.4, 35.0],
  // ── África ──
  MAR: [ 31.8, -7.0],
  DZA: [ 28.0,  2.5],
  TUN: [ 34.0,  9.0],
  LBY: [ 27.0, 17.0],
  EGY: [ 26.0, 30.0],
  SDN: [ 15.0, 30.0],
  SSD: [  7.5, 30.0],
  ETH: [  9.0, 40.5],
  ERI: [ 15.2, 39.5],
  KEN: [ -0.5, 37.8],
  TZA: [ -6.5, 35.0],
  UGA: [  1.4, 32.5],
  RWA: [ -2.0, 30.0],
  BDI: [ -3.4, 29.9],
  MOZ: [-18.5, 35.5],
  ZMB: [-13.5, 27.5],
  ZWE: [-19.0, 29.5],
  NAM: [-22.0, 18.0],
  BWA: [-22.3, 24.7],
  ZAF: [-29.0, 25.0],
  LSO: [-29.6, 28.2],
  SWZ: [-26.5, 31.5],
  AGO: [-11.5, 17.5],
  COD: [ -4.0, 24.0],
  COG: [ -0.5, 15.5],
  CAF: [  7.0, 21.0],
  CMR: [  5.7, 12.7],
  NGA: [  9.0,  8.0],
  GHA: [  8.0,  -1.0],
  CIV: [  7.5, -5.5],
  SEN: [ 14.5,-14.5],
  MLI: [ 17.5,  -4.0],
  BFA: [ 12.4,  -1.5],
  NER: [ 17.5,   8.0],
  TCD: [ 15.0, 18.5],
  MRT: [ 20.0,-11.0],
  SOM: [  6.0, 46.0],
  MDG: [-20.0, 47.0],
  // Ilhas africanas
  CPV: [ 16.0,-24.0],
  SYC: [ -4.7, 55.5],
  COM: [-11.6, 43.3],
  MUS: [-20.3, 57.6],
  // ── Oceania ──
  AUS: [-25.5,134.0],
  NZL: [-41.0,174.0],
  PNG: [ -6.0,145.0],
  FJI: [-17.7,178.0],
  PLW: [  7.5,134.6],
  KIR: [  1.0,-157.0],
  SLB: [ -8.5,160.0],
  VUT: [-16.0,167.5],
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

// SW / NE corners for each region — tight bounds so flyToBounds zooms close
const REGION_BOUNDS = {
  "americas": [[-55, -118], [ 70,  -35]],
  "europe":   [[ 35,  -22], [ 71,   42]],
  "africa":   [[-35,  -17], [ 37,   51]],
  "asia":     [[  1,   26], [ 77,  148]],
  "oceania":  [[-47,  112], [ 20,  180]],
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

  // Zoom animado ao continente selecionado; volta à visão mundial ao limpar
  if (region && REGION_BOUNDS[region]) {
    map.flyToBounds(REGION_BOUNDS[region], {
      padding: [10, 10],
      maxZoom: 5,
      animate: true,
      duration: 0.9,
    });
  } else if (!region) {
    map.flyTo([20, 15], 2, { animate: true, duration: 0.9 });
  }
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
    addTextMarker(pos, RBi18n.t(text), "np-ocean-label");
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

  if (btn) { btn.disabled = true; btn.textContent = RBi18n.t("Gerando…"); }

  // Hide non-signatory country labels to avoid visual clutter in the print
  const hiddenLabels = [];
  labelMarkers.forEach(({ marker, signatory }) => {
    if (!signatory && map.hasLayer(marker)) {
      map.removeLayer(marker);
      hiddenLabels.push(marker);
    }
  });

  try {
    const canvas = await html2canvas(mapContainer, {
      useCORS: true,
      allowTaint: true,
      scale: 2,
      backgroundColor: "#101d4f",
    });
    const link = document.createElement("a");
    link.download = "radar-brasil-nota-pais.png";
    link.href = canvas.toDataURL("image/png");
    link.click();
  } catch (err) {
    console.error("Erro ao gerar imagem:", err);
  } finally {
    // Restore non-signatory labels
    hiddenLabels.forEach(marker => marker.addTo(map));

    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg> ${RBi18n.t("Print Mapa")}`;
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
  if (RBi18n.getLang() === "en") {
    return props.NAME || props.ADMIN || props.name || NOMES_PT[iso] || "";
  }
  return NOMES_PT[iso] || props.NAME || props.ADMIN || props.name || "";
}

function getContinent(props) {
  const raw = props.CONTINENT || props.continent || "";
  if (raw && CONTINENT_COLORS[raw]) return raw;
  return ISO_CONTINENT[getIso(props)] || "Other";
}

function ringArea(ring) {
  let area = 0;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    area += (ring[j][0] + ring[i][0]) * (ring[j][1] - ring[i][1]);
  }
  return Math.abs(area / 2);
}

function getCentroid(feature) {
  const geom = feature.geometry;
  if (!geom) return null;
  let ring = [];
  if (geom.type === "Polygon") {
    ring = geom.coordinates[0];
  } else if (geom.type === "MultiPolygon") {
    let maxArea = 0;
    geom.coordinates.forEach(poly => {
      const a = ringArea(poly[0]);
      if (a > maxArea) { maxArea = a; ring = poly[0]; }
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
  // Canvas renderer prevents html2canvas from losing SVG layers in print
  const countriesRenderer = L.canvas({ padding: 0.5 });

  geoLayer = L.geoJSON(data, {
    renderer: countriesRenderer,
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
        ? `<strong>${RBi18n.t("Nota")}</strong><br>${name}: ${RBi18n.t(nota)}`
        : RBi18n.t("Nota não atribuída");

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

    const centroid = LABEL_OVERRIDES[iso] || getCentroid(feature);
    if (!centroid) return;

    const pin = L.marker(centroid, { icon: PIN_ICON, interactive: false, zIndexOffset: 500 }).addTo(map);
    const featureContinent = getContinent(feature.properties);
    pinMarkers.push({ marker: pin, continent: featureContinent });

    const name = getName(feature.properties);
    if (name) {
      const lbl = addTextMarker([centroid[0] - 1.8, centroid[1]], name, "np-country-label");
      labelMarkers.push({ marker: lbl, continent: featureContinent, signatory: true });
    }
  });

  // Country name labels (non-signatories)
  data.features.forEach(feature => {
    const iso = getIso(feature.properties);
    if (!iso || CHAMP_SIGNATORIES.has(iso)) return;

    const centroid = LABEL_OVERRIDES[iso] || getCentroid(feature);
    if (!centroid) return;

    const name = getName(feature.properties);
    if (!name) return;

    const featureContinent = getContinent(feature.properties);
    const lbl = addTextMarker(centroid, name, "np-country-label np-country-label--minor");
    labelMarkers.push({ marker: lbl, continent: featureContinent, signatory: false });
  });
}

// ── BOOT ──────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", init);

