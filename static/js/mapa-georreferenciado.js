/* Mapa Georreferenciado – Radar Brasil */
/* global L */

const COR_FINANCIAMENTO     = "#264584"; // Azul – tem financiamento
const COR_SEM_FINANCIAMENTO = "#F4511E"; // Laranja-vermelho – sem financiamento

// Limites aproximados do Brasil
const BR_BOUNDS = L.latLngBounds(
    L.latLng(-35.0, -74.0),
    L.latLng(5.5,  -28.5)
);

// Mapeamento fixo região → siglas de UF
const REGIAO_UFS = {
    "Norte":        ["AC", "AM", "AP", "PA", "RO", "RR", "TO"],
    "Nordeste":     ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Centro-Oeste": ["DF", "GO", "MS", "MT"],
    "Sudeste":      ["ES", "MG", "RJ", "SP"],
    "Sul":          ["PR", "RS", "SC"],
};

let map, allFeatures = [], markerLayer, canvasRenderer;
let activeFilters = {};
let allUfOptions = [];

// ── Polígono simplificado do Brasil (Natural Earth) ────────────
const BRAZIL_POLY = { type: "Feature", geometry: { type: "Polygon", coordinates: [[
    [-60.19, 5.27],  [-60.70, 4.20],  [-60.66, 1.32],  [-59.84, 1.38],
    [-57.96, 1.21],  [-54.53, 2.13],  [-51.62, 4.22],  [-51.40, 1.46],
    [-50.07,-0.34],  [-48.48,-1.46],  [-46.82,-1.06],  [-44.36,-2.46],
    [-41.73,-2.91],  [-38.50,-3.72],  [-36.54,-4.50],  [-35.19,-5.81],
    [-34.79,-7.12],  [-34.86,-8.10],  [-36.50,-9.00],  [-37.50,-10.47],
    [-38.50,-13.00], [-39.08,-17.02], [-40.26,-20.19], [-43.18,-22.90],
    [-44.72,-23.00], [-46.32,-24.00], [-48.59,-27.59], [-50.52,-29.00],
    [-51.21,-31.05], [-52.01,-33.61], [-53.37,-33.75], [-55.50,-31.00],
    [-57.00,-29.70], [-55.60,-27.50], [-54.62,-25.49], [-54.80,-22.30],
    [-57.90,-22.00], [-57.90,-17.80], [-60.13,-16.26], [-65.33,-15.00],
    [-68.74,-11.01], [-70.29,-11.00], [-73.90, -7.47], [-70.47, -2.00],
    [-70.02, -0.19], [-69.98,  0.71], [-69.94,  1.74], [-67.33,  2.00],
    [-64.50,  4.00], [-63.39,  3.93], [-61.54,  4.27], [-60.19,  5.27],
]] }, properties: {} };

// ── Inicializa o mapa ──────────────────────────────────────────
function initMap() {
    map = L.map("mg-map", {
        center: [-14.2, -51.9],
        zoom: 4,
        minZoom: 4,
        maxZoom: 14,
        zoomControl: true,
    });

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 19,
            attribution:
                '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> ' + RBi18n.t("contribuidores"),
        }
    ).addTo(map);

    // Pane exclusivo para o overlay do Brasil (abaixo dos marcadores z=400)
    // Canvas renderer evita o deslocamento no html2canvas: SVG paths sofrem do
    // bug de translate3d herdado do .leaflet-map-pane; canvas é capturado corretamente.
    map.createPane('brasilPane').style.zIndex = 210;
    const brasilRenderer = L.canvas({ pane: 'brasilPane', padding: 0.5 });
    L.geoJSON(BRAZIL_POLY, {
        pane:     'brasilPane',
        renderer: brasilRenderer,
        style: {
            fillColor:   '#264584',
            fillOpacity: 0.22,
            color:       '#264584',
            weight:      1.2,
            opacity:     0.50,
        },
    }).addTo(map);

    canvasRenderer = L.canvas({ padding: 0.5 });
    markerLayer = L.featureGroup().addTo(map);

    // ── Centraliza o popup ao clicar num município ────────────────
    map.on('popupopen', function (e) {
        requestAnimationFrame(function () {
            const latlng   = e.popup.getLatLng();
            const el       = e.popup.getElement();
            const mapSize  = map.getSize();
            const markerPx = map.latLngToContainerPoint(latlng);

            // Altura real do popup (+24px para a ponta e margem de segurança)
            const popupH  = el ? el.offsetHeight + 24 : 200;

            // Alvo vertical: marker fica na posição que coloca o popup centrado
            // (capped em 75% da altura para não empurrar o marker fora da tela)
            const targetY = Math.min(mapSize.y * 0.75, mapSize.y / 2 + popupH / 2);

            // Alvo horizontal: centro da área do mapa
            const targetX = mapSize.x / 2;

            map.panBy(
                [markerPx.x - targetX, markerPx.y - targetY],
                { animate: true, duration: 0.45 }
            );
        });
    });
}

// ── Carrega filtros e popula selects ──────────────────────────
async function carregarFiltros() {
    try {
        const resp = await fetch("/indicadores/api/mapa/filtros/");
        const data = await resp.json();

        const t = RBi18n.t;
        populateSelect("mg-f-eixo",       data.eixos,       t("Todos"));
        populateSelect("mg-f-modalidade", data.modalidades,  t("Todas as Modalidades"));
        populateSelect("mg-f-estagio",    data.estagios,     t("Todos os Estágios"));
        populateSelect("mg-f-executor",   data.executores,   t("Todos os Executores"));
        populateSelect("mg-f-regiao",     data.regioes,      t("Todas as Regiões"));
        populateSelect("mg-f-uf",         data.ufs,          t("Todos os Estados"));

        const ufSel = document.getElementById("mg-f-uf");
        allUfOptions = Array.from(ufSel.options).slice(1).map(o => ({ value: o.value, text: o.textContent }));

        buildLegend();
    } catch (e) {
        console.error("Erro filtros:", e);
    }
}

function populateSelect(id, items, placeholder) {
    const sel = document.getElementById(id);
    if (!sel) return;
    sel.innerHTML = `<option value="">${placeholder}</option>`;
    (items || []).forEach(v => {
        const opt = document.createElement("option");
        opt.value = v; opt.textContent = v;
        sel.appendChild(opt);
    });
}

// ── Carrega dados do mapa ──────────────────────────────────────
async function carregarDados() {
    mostrarLoader(true);
    try {
        const resp = await fetch("/indicadores/api/mapa/dados/");
        const geo  = await resp.json();
        allFeatures = (geo.features || []);
        filtrar();
    } catch (e) {
        console.error("Erro dados mapa:", e);
    } finally {
        mostrarLoader(false);
    }
}

// Raio por porte populacional (replica R: rescale(populacao, to = c(5, 25)))
function _radiusByPorte(porte) {
    if (porte === "Capital")        return 20;
    if (porte === "Acima de 80mil") return 11;
    return 5;  // Abaixo de 80mil ou desconhecido
}

// ── Renderiza marcadores no mapa ───────────────────────────────
function renderMarkers(features, fitBounds) {
    markerLayer.clearLayers();

    // Sem financiamento renderiza primeiro (embaixo); com financiamento por último (em cima)
    const sorted = [...features].sort((a, b) =>
        (a.properties.tem_financiamento ? 1 : 0) - (b.properties.tem_financiamento ? 1 : 0)
    );

    sorted.forEach(feat => {
        const p   = feat.properties;
        const cor = p.tem_financiamento ? COR_FINANCIAMENTO : COR_SEM_FINANCIAMENTO;
        const [lng, lat] = feat.geometry.coordinates;

        const marker = L.circleMarker([lat, lng], {
            renderer:    canvasRenderer,
            radius:      _radiusByPorte(p.porte),
            fillColor:   cor,
            color:       "#ffffff",
            weight:      1,
            fillOpacity: 0.90,
            opacity:     1,
        });

        marker.bindPopup(buildPopup(p), {
            maxWidth: 400,
            minWidth: 320,
            autoPanPaddingTopLeft:     L.point(20, 80),
            autoPanPaddingBottomRight: L.point(20, 20),
        });
        markerLayer.addLayer(marker);
    });

    atualizarStats(features);

    if (fitBounds && features.length > 0 && markerLayer.getLayers().length > 0) {
        try {
            map.fitBounds(markerLayer.getBounds().pad(0.3), { maxZoom: 10 });
        } catch (_) {}
    }
}

function _svgIcon(path) {
    return `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${path}</svg>`;
}
const _IC = {
    porte:  _svgIcon('<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>'),
    perfil: _svgIcon('<circle cx="12" cy="8" r="4"/><path d="M20 21a8 8 0 1 0-16 0"/>'),
    emp:    _svgIcon('<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>'),
    valor:  _svgIcon('<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'),
    exec:   _svgIcon('<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>'),
    regiao: _svgIcon('<circle cx="12" cy="12" r="10"/><polyline points="2 12 12 12 17 17"/>'),
};

function _fmtValor(est) {
    if (!est || est <= 0) return "—";
    return `R$ ${Number(est).toLocaleString("pt-BR")}`;
}

function buildPopup(p) {
    const fmt = v => (v && v !== "nan") ? v : "—";

    const t = RBi18n.t;
    if (!p.tem_financiamento) {
        return `
        <div class="mg-popup">
          <div class="mg-popup-header">
            <h4>${fmt(p.municipio)}<span class="mg-popup-uf"> — ${fmt(p.uf)}</span></h4>
            <span class="mg-popup-status-tag mg-popup-status-no">${t("Sem Financiamento")}</span>
          </div>
          <div class="mg-popup-body">
            <div class="mg-popup-row">
              <span class="mg-popup-icon">${_IC.porte}</span>
              <span class="mg-popup-lbl">${t("Porte Populacional")}</span>
              <span class="mg-popup-val">${t(fmt(p.porte))}</span>
            </div>
            ${p.populacao ? `
            <div class="mg-popup-row">
              <span class="mg-popup-icon">${_IC.perfil}</span>
              <span class="mg-popup-lbl">${t("População")}</span>
              <span class="mg-popup-val">${Number(p.populacao).toLocaleString("pt-BR")}</span>
            </div>` : ""}
            <div class="mg-popup-row">
              <span class="mg-popup-icon">${_IC.regiao}</span>
              <span class="mg-popup-lbl">${t("Região")}</span>
              <span class="mg-popup-val">${t(fmt(p.regiao))}</span>
            </div>
          </div>
        </div>`;
    }

    const programas = (p.programas || []).filter(prog => {
        if (activeFilters.estagio    && prog.estagio    !== activeFilters.estagio)    return false;
        if (activeFilters.executor   && prog.executor   !== activeFilters.executor)   return false;
        if (activeFilters.modalidade && prog.modalidade !== activeFilters.modalidade) return false;
        if (activeFilters.eixo       && prog.eixo       !== activeFilters.eixo)       return false;
        return true;
    });
    const nProg = programas.length || p.n_programas || 1;

    const progsHtml = programas.map((prog, i) => {
        const pct = Math.min(Number(prog.percentual) || 0, 100);
        const nome = (prog.empreendimento && prog.empreendimento !== "nan")
            ? prog.empreendimento : "—";
        const estagio = (prog.estagio && prog.estagio !== "nan") ? prog.estagio : "";
        return `
        <div class="mg-popup-prog-item${i > 0 ? " mg-popup-prog-item--sep" : ""}">
          <div class="mg-popup-prog-name">${nome}</div>
          <div class="mg-popup-prog-meta">
            ${estagio ? `<span class="mg-popup-status-tag mg-popup-status-yes">${estagio}</span>` : ""}
            <span class="mg-popup-prog-valor">${_fmtValor(prog.estimativa)}</span>
          </div>
          <div class="mg-popup-exec-wrap">
            <span class="mg-popup-prog-track">
              <span class="mg-popup-prog-fill" style="width:${pct}%"></span>
            </span>
            <span class="mg-popup-pct">${pct}%</span>
          </div>
        </div>`;
    }).join("");

    const countLabel = nProg === 1
        ? `1 ${t("programa de investimento")}`
        : `${nProg} ${t("programas de investimento")}`;

    const estimativaTotal = p.estimativa_total > 0 ? _fmtValor(p.estimativa_total) : "—";

    return `
    <div class="mg-popup">
      <div class="mg-popup-header">
        <h4>${fmt(p.municipio)}<span class="mg-popup-uf"> — ${fmt(p.uf)}</span></h4>
        <span class="mg-popup-count-badge">${countLabel}</span>
      </div>
      <div class="mg-popup-body">
        <div class="mg-popup-row">
          <span class="mg-popup-icon">${_IC.porte}</span>
          <span class="mg-popup-lbl">${t("Porte Populacional")}</span>
          <span class="mg-popup-val">${t(fmt(p.porte))}</span>
        </div>
        ${p.populacao ? `
        <div class="mg-popup-row">
          <span class="mg-popup-icon">${_IC.perfil}</span>
          <span class="mg-popup-lbl">${t("População")}</span>
          <span class="mg-popup-val">${Number(p.populacao).toLocaleString("pt-BR")}</span>
        </div>` : ""}
        ${p.perfil ? `
        <div class="mg-popup-row">
          <span class="mg-popup-icon">${_IC.emp}</span>
          <span class="mg-popup-lbl">${t("Perfil Investimento")}</span>
          <span class="mg-popup-val">${t(fmt(p.perfil))}</span>
        </div>` : ""}
        <div class="mg-popup-row">
          <span class="mg-popup-icon">${_IC.valor}</span>
          <span class="mg-popup-lbl">${t("Estimativa Total")}</span>
          <span class="mg-popup-val">${estimativaTotal}</span>
        </div>
        <div class="mg-popup-progs${programas.length > 3 ? " mg-popup-progs--scroll" : ""}">
          ${progsHtml}
        </div>
      </div>
    </div>`;
}

// ── Filtros client-side ────────────────────────────────────────
function filtrar() {
    const eixo         = document.getElementById("mg-f-eixo")?.value       || "";
    const modalidade   = document.getElementById("mg-f-modalidade")?.value  || "";
    const estagio      = document.getElementById("mg-f-estagio")?.value     || "";
    const executor     = document.getElementById("mg-f-executor")?.value    || "";
    const regiao       = document.getElementById("mg-f-regiao")?.value      || "";
    const uf           = document.getElementById("mg-f-uf")?.value          || "";
    const porte        = document.getElementById("mg-f-porte")?.value       || "";
    const mun          = (document.getElementById("mg-f-municipio")?.value || "").toLowerCase().trim();
    const exibirSemFin = document.getElementById("mg-f-sem-financiamento")?.checked || false;

    activeFilters = { eixo, modalidade, estagio, executor };

    const filtroFinanciamento = eixo || modalidade || estagio || executor;

    const filtered = allFeatures.filter(f => {
        const p = f.properties;

        if (!p.tem_financiamento) {
            if (!exibirSemFin)        return false; // oculto por padrão
            if (filtroFinanciamento)  return false;
            if (regiao && p.regiao !== regiao) return false;
            if (uf     && p.uf     !== uf)     return false;
            if (porte  && p.porte  !== porte)  return false;
            if (mun    && !(p.municipio || "").toLowerCase().includes(mun)) return false;
            return true;
        }

        if (eixo       && !(p.eixos       || []).includes(eixo))       return false;
        if (modalidade && !(p.modalidades || []).includes(modalidade)) return false;
        if (estagio    && !(p.estagios    || []).includes(estagio))    return false;
        if (executor   && !(p.executores  || []).includes(executor))   return false;
        if (regiao     && p.regiao !== regiao)                         return false;
        if (uf         && p.uf     !== uf)                             return false;
        if (porte      && p.porte  !== porte)                          return false;
        if (mun        && !(p.municipio || "").toLowerCase().includes(mun)) return false;
        return true;
    });

    const algumFiltroAtivo = eixo || modalidade || estagio || executor ||
                             regiao || uf || porte || mun;
    renderMarkers(filtered, !!algumFiltroAtivo);

    const legendSemFin = document.getElementById("mg-legend-sem-fin");
    if (legendSemFin) legendSemFin.style.display = exibirSemFin ? "" : "none";

    _atualizarBadgeFiltros();
}

function atualizarEstadosPorRegiao(regiao) {
    const sel = document.getElementById("mg-f-uf");
    if (!sel) return;
    const ufsFiltrados = regiao ? (REGIAO_UFS[regiao] || []) : null;
    const currentVal = sel.value;
    sel.innerHTML = `<option value="">${RBi18n.t("Todos os Estados")}</option>`;
    const opcoes = ufsFiltrados
        ? allUfOptions.filter(o => ufsFiltrados.includes(o.value))
        : allUfOptions;
    opcoes.forEach(o => {
        const opt = document.createElement("option");
        opt.value = o.value;
        opt.textContent = o.text;
        sel.appendChild(opt);
    });
    sel.value = (ufsFiltrados && !ufsFiltrados.includes(currentVal)) ? "" : currentVal;
}

function limparFiltros() {
    ["mg-f-eixo","mg-f-modalidade","mg-f-estagio","mg-f-executor",
     "mg-f-regiao","mg-f-uf","mg-f-porte"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
    atualizarEstadosPorRegiao("");
    const mun = document.getElementById("mg-f-municipio");
    if (mun) mun.value = "";
    const munClearBtn = document.getElementById("mg-f-municipio-clear");
    if (munClearBtn) munClearBtn.hidden = true;
    const toggle = document.getElementById("mg-f-sem-financiamento");
    if (toggle) toggle.checked = false;
    map.fitBounds(BR_BOUNDS);
    filtrar();
}

// ── Badge de filtros ativos ────────────────────────────────────
function _atualizarBadgeFiltros() {
    const ids = ["mg-f-eixo","mg-f-modalidade","mg-f-estagio","mg-f-executor",
                 "mg-f-regiao","mg-f-uf","mg-f-porte"];
    let count = ids.reduce((n, id) => {
        const el = document.getElementById(id);
        return n + (el && el.value ? 1 : 0);
    }, 0);
    const munEl = document.getElementById("mg-f-municipio");
    if (munEl && munEl.value.trim()) count++;
    const badge = document.getElementById("mg-filter-count");
    if (badge) { badge.textContent = count; badge.hidden = count === 0; }
}

// ── localStorage – filtros persistentes ───────────────────────

// ── Painel de totais ───────────────────────────────────────────
function atualizarStats(features) {
    // Replica lógica do app R:
    // Investimento Único  → mínimo por município
    // Investimento Agrupado → 1x por empreendimento (já pré-calculado no backend)
    const unicoMunis = new Map();  // code_muni → unico_min_est
    const agrupEmps  = new Map();  // empreendimento → estimativa

    features.forEach(f => {
        const p = f.properties;
        if (!p.tem_financiamento) return;

        const key = p.code_muni || p.municipio;
        if (p.unico_min_est > 0) {
            unicoMunis.set(key, p.unico_min_est);
        }

        (p.agrupado_empreendimentos || []).forEach(emp => {
            if (!agrupEmps.has(emp.nome)) {
                agrupEmps.set(emp.nome, emp.estimativa);
            }
        });
    });

    const total =
        Array.from(unicoMunis.values()).reduce((s, v) => s + v, 0) +
        Array.from(agrupEmps.values()).reduce((s, v) => s + v, 0);

    const munis = features.filter(f => f.properties.tem_financiamento).length;

    const elValor = document.getElementById("mg-stats-valor");
    const elMunis = document.getElementById("mg-stats-municipios");

    if (elValor) {
        elValor.textContent = total > 0
            ? `R$ ${Number(total).toLocaleString("pt-BR", { minimumFractionDigits: 0 })}`
            : "—";
    }
    if (elMunis) {
        const t = RBi18n.t;
        const munLabel = munis !== 1 ? t("municípios") : t("Município");
        elMunis.textContent = `${t("Para")} ${munis.toLocaleString("pt-BR")} ${munLabel}`;
    }
}

// ── Legenda ────────────────────────────────────────────────────
function buildLegend() {
    const body = document.getElementById("mg-legend-body");
    if (!body) return;
    const t = RBi18n.t;
    body.innerHTML = `
      <div class="mg-legend-item">
        <span class="mg-legend-dot" style="background:${COR_FINANCIAMENTO};"></span>
        <span>${t("Financiamento")}</span>
      </div>
      <div class="mg-legend-item" id="mg-legend-sem-fin" style="display:none">
        <span class="mg-legend-dot" style="background:${COR_SEM_FINANCIAMENTO};"></span>
        <span>${t("Sem Financiamento")}</span>
      </div>
      <div class="mg-legend-size">
        <div class="mg-legend-size-row">
          <div class="mg-legend-size-item">
            <span class="mg-legend-circle" style="width:10px;height:10px;"></span>
            <span class="mg-legend-size-label">${t("Abaixo 80k")}</span>
          </div>
          <div class="mg-legend-size-item">
            <span class="mg-legend-circle" style="width:22px;height:22px;"></span>
            <span class="mg-legend-size-label">${t("Acima 80k")}</span>
          </div>
          <div class="mg-legend-size-item">
            <span class="mg-legend-circle" style="width:40px;height:40px;"></span>
            <span class="mg-legend-size-label">${t("Capital")}</span>
          </div>
        </div>
      </div>`;
}

// ── Utilitários ────────────────────────────────────────────────
function mostrarLoader(vis) {
    const el = document.getElementById("mg-loader");
    if (el) el.classList.toggle("hidden", !vis);
}

async function imprimirMapa() {
    const btn = document.getElementById("mg-btn-print");
    const mapArea = document.querySelector(".mg-map-area");
    if (!mapArea) return;

    if (btn) { btn.disabled = true; btn.textContent = RBi18n.t("Gerando…"); }
    mostrarLoader(true);

    try {
        const canvas = await html2canvas(mapArea, {
            useCORS: true,
            allowTaint: true,
            scale: 2,
            backgroundColor: "#e8f2f6",
            ignoreElements: el => el.id === "mg-loader",
        });
        const link = document.createElement("a");
        link.download = "radar-brasil-mapa.png";
        link.href = canvas.toDataURL("image/png");
        link.click();
    } catch (err) {
        console.error("Erro ao gerar imagem:", err);
    } finally {
        mostrarLoader(false);
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg> ${RBi18n.t("Print Mapa")}`;
        }
    }
}

function baixarDados() {
    const eixo  = document.getElementById("mg-f-eixo")?.value  || "";
    const uf    = document.getElementById("mg-f-uf")?.value    || "";
    const porte = document.getElementById("mg-f-porte")?.value || "";
    const mun   = (document.getElementById("mg-f-municipio")?.value || "").toLowerCase().trim();

    const filtered = allFeatures.filter(f => {
        const p = f.properties;
        if (!p.tem_financiamento) return false;  // exporta só municípios com dados
        if (eixo  && !(p.eixos  || []).includes(eixo)) return false;
        if (uf    && p.uf    !== uf)    return false;
        if (porte && p.porte !== porte) return false;
        if (mun   && !(p.municipio || "").toLowerCase().includes(mun)) return false;
        return true;
    });

    const t = RBi18n.t;
    const header = [t("Município"),t("UF"),t("Região"),t("Empreendimento"),t("Modalidade"),t("Executor"),
                    t("Estágio"),t("Estimativa 2023-2030"),t("% Executado"),t("Porte Populacional"),t("Eixo")];
    const rows = filtered.map(f => {
        const p = f.properties;
        return [p.municipio, p.uf, p.regiao, p.empreendimento, p.modalidade,
                p.executor, p.estagio, p.estimativa, p.percentual, p.perfil, p.eixo]
            .map(v => `"${String(v ?? "").replace(/"/g, '""')}"`).join(",");
    });

    const csv  = [header.join(","), ...rows].join("\n");
    const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href = url; a.download = "radar-brasil-mapa.csv";
    a.click();
    URL.revokeObjectURL(url);
}

// ── Bootstrap ──────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
    initMap();
    await carregarFiltros();
    await carregarDados();

    ["mg-f-eixo","mg-f-modalidade","mg-f-estagio","mg-f-executor","mg-f-uf","mg-f-porte"].forEach(id => {
        document.getElementById(id)?.addEventListener("change", filtrar);
    });
    document.getElementById("mg-f-regiao")?.addEventListener("change", e => {
        atualizarEstadosPorRegiao(e.target.value);
        filtrar();
    });
    const munInput = document.getElementById("mg-f-municipio");
    const munClear = document.getElementById("mg-f-municipio-clear");
    munInput?.addEventListener("input", () => {
        if (munClear) munClear.hidden = !munInput.value;
        filtrar();
    });
    munClear?.addEventListener("click", () => {
        if (munInput) munInput.value = "";
        munClear.hidden = true;
        munInput?.focus();
        filtrar();
    });
    document.getElementById("mg-f-sem-financiamento")?.addEventListener("change", filtrar);
    document.getElementById("mg-btn-limpar")?.addEventListener("click", limparFiltros);
    document.getElementById("mg-btn-print")?.addEventListener("click", imprimirMapa);
    document.getElementById("mg-btn-baixar")?.addEventListener("click", baixarDados);
});
