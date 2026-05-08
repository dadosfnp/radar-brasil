/* Mapa Georreferenciado – Radar Brasil */
/* global L */

const COR_EIXO = [
    "#2196F3","#4CAF50","#FF9800","#E91E63","#9C27B0","#00BCD4","#FF5722"
];

// Limites aproximados do Brasil
const BR_BOUNDS = L.latLngBounds(
    L.latLng(-35.0, -74.0),
    L.latLng(5.5,  -28.5)
);

let map, allFeatures = [], markerLayer, eixoCores = {};

// ── Inicializa o mapa ──────────────────────────────────────────
function initMap() {
    map = L.map("mg-map", {
        center: [-14.2, -51.9],
        zoom: 4,
        minZoom: 4,
        maxZoom: 14,
        maxBounds: BR_BOUNDS,
        maxBoundsViscosity: 0.9,
        zoomControl: true,
    });

    L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
        {
            attribution:
                '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
                '&copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: "abcd",
            maxZoom: 19,
        }
    ).addTo(map);

    markerLayer = L.featureGroup().addTo(map);
}

// ── Carrega filtros e popula selects ──────────────────────────
async function carregarFiltros() {
    try {
        const resp = await fetch("/indicadores/api/mapa/filtros/");
        const data = await resp.json();

        populateSelect("mg-f-eixo",       data.eixos,      "Todos");
        populateSelect("mg-f-modalidade", data.modalidades, "Todas as Modalidades");
        populateSelect("mg-f-estagio",    data.estagios,    "Todos os Estágios");
        populateSelect("mg-f-executor",   data.executores,  "Todos os Executores");
        populateSelect("mg-f-regiao",     data.regioes,     "Todas as Regiões");
        populateSelect("mg-f-uf",         data.ufs,         "Todos os Estados");

        (data.eixos || []).forEach((e, i) => {
            eixoCores[e] = COR_EIXO[i % COR_EIXO.length];
        });

        buildLegend(data.eixos || []);
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
        renderMarkers(allFeatures, false);
    } catch (e) {
        console.error("Erro dados mapa:", e);
    } finally {
        mostrarLoader(false);
    }
}

// ── Renderiza marcadores no mapa ───────────────────────────────
function renderMarkers(features, fitBounds) {
    markerLayer.clearLayers();

    features.forEach(feat => {
        const p   = feat.properties;
        const cor = eixoCores[p.eixo] || "#4CAF50";
        const [lng, lat] = feat.geometry.coordinates;

        const marker = L.circleMarker([lat, lng], {
            radius: 6,
            fillColor: cor,
            color: "#fff",
            weight: 1.2,
            fillOpacity: 0.88,
        });

        marker.bindPopup(buildPopup(p), { maxWidth: 300 });
        markerLayer.addLayer(marker);
    });

    atualizarStats(features);

    if (fitBounds && features.length > 0 && markerLayer.getLayers().length > 0) {
        try {
            map.fitBounds(markerLayer.getBounds().pad(0.3), { maxZoom: 10 });
        } catch (_) {}
    }
}

function buildPopup(p) {
    const fmt   = v => (v && v !== "nan") ? v : "—";
    const valor = p.estimativa > 0
        ? `R$ ${Number(p.estimativa).toLocaleString("pt-BR")}` : "—";
    const cor   = eixoCores[p.eixo] || "#4CAF50";

    return `
    <div class="mg-popup">
      <h4>${fmt(p.municipio)} – ${fmt(p.uf)}</h4>
      <div class="mg-popup-row"><span class="mg-popup-label">Empreendimento:</span> ${fmt(p.empreendimento)}</div>
      <div class="mg-popup-row"><span class="mg-popup-label">Modalidade:</span> ${fmt(p.modalidade)}</div>
      <div class="mg-popup-row"><span class="mg-popup-label">Executor:</span> ${fmt(p.executor)}</div>
      <div class="mg-popup-row"><span class="mg-popup-label">Estimativa:</span> ${valor}</div>
      <div class="mg-popup-row"><span class="mg-popup-label">Execução:</span> ${p.percentual || 0}%</div>
      <span class="mg-popup-tag" style="background:${cor};color:#fff;">${fmt(p.estagio)}</span>
    </div>`;
}

// ── Filtros client-side ────────────────────────────────────────
function filtrar() {
    const eixo       = document.getElementById("mg-f-eixo")?.value       || "";
    const modalidade = document.getElementById("mg-f-modalidade")?.value  || "";
    const estagio    = document.getElementById("mg-f-estagio")?.value     || "";
    const executor   = document.getElementById("mg-f-executor")?.value    || "";
    const regiao     = document.getElementById("mg-f-regiao")?.value      || "";
    const uf         = document.getElementById("mg-f-uf")?.value          || "";
    const porte      = document.getElementById("mg-f-porte")?.value       || "";
    const mun        = (document.getElementById("mg-f-municipio")?.value || "").toLowerCase().trim();

    const filtered = allFeatures.filter(f => {
        const p = f.properties;
        if (eixo       && p.eixo       !== eixo)       return false;
        if (modalidade && p.modalidade !== modalidade) return false;
        if (estagio    && p.estagio    !== estagio)    return false;
        if (executor   && p.executor   !== executor)   return false;
        if (regiao     && p.regiao     !== regiao)     return false;
        if (uf         && p.uf         !== uf)         return false;
        if (porte      && p.porte      !== porte)      return false;
        if (mun        && !(p.municipio || "").toLowerCase().includes(mun)) return false;
        return true;
    });

    const algumFiltroAtivo = eixo || modalidade || estagio || executor ||
                             regiao || uf || porte || mun;
    renderMarkers(filtered, !!algumFiltroAtivo);
}

function limparFiltros() {
    ["mg-f-eixo","mg-f-modalidade","mg-f-estagio","mg-f-executor",
     "mg-f-regiao","mg-f-uf","mg-f-porte"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
    const mun = document.getElementById("mg-f-municipio");
    if (mun) mun.value = "";
    map.fitBounds(BR_BOUNDS);
    renderMarkers(allFeatures, false);
}

// ── Painel de totais ───────────────────────────────────────────
function atualizarStats(features) {
    const total = features.reduce((s, f) => s + (f.properties.estimativa || 0), 0);
    const munis = new Set(features.map(f => f.properties.code_muni || f.properties.municipio)).size;

    const elValor = document.getElementById("mg-stats-valor");
    const elMunis = document.getElementById("mg-stats-municipios");

    if (elValor) {
        elValor.textContent = total > 0
            ? `R$ ${Number(total).toLocaleString("pt-BR", { minimumFractionDigits: 0 })}`
            : "—";
    }
    if (elMunis) {
        elMunis.textContent = `Para ${munis.toLocaleString("pt-BR")} Município${munis !== 1 ? "s" : ""}`;
    }
}

// ── Legenda ────────────────────────────────────────────────────
function buildLegend(eixos) {
    const body = document.getElementById("mg-legend-body");
    if (!body) return;
    body.innerHTML = "";
    if (!eixos.length) {
        body.innerHTML = `
          <div class="mg-legend-item">
            <span class="mg-legend-dot" style="background:#4CAF50;"></span>
            <span>Municípios com financiamento</span>
          </div>`;
        return;
    }
    eixos.forEach(e => {
        const cor   = eixoCores[e] || "#4CAF50";
        const short = e.length > 38 ? e.substring(0, 36) + "…" : e;
        body.innerHTML += `
          <div class="mg-legend-item">
            <span class="mg-legend-dot" style="background:${cor};"></span>
            <span>${short}</span>
          </div>`;
    });
}

// ── Utilitários ────────────────────────────────────────────────
function mostrarLoader(vis) {
    const el = document.getElementById("mg-loader");
    if (el) el.classList.toggle("hidden", !vis);
}

function imprimirMapa() {
    window.print();
}

function baixarDados() {
    const eixo  = document.getElementById("mg-f-eixo")?.value  || "";
    const uf    = document.getElementById("mg-f-uf")?.value    || "";
    const porte = document.getElementById("mg-f-porte")?.value || "";
    const mun   = (document.getElementById("mg-f-municipio")?.value || "").toLowerCase().trim();

    const filtered = allFeatures.filter(f => {
        const p = f.properties;
        if (eixo  && p.eixo  !== eixo)  return false;
        if (uf    && p.uf    !== uf)    return false;
        if (porte && p.porte !== porte) return false;
        if (mun   && !(p.municipio || "").toLowerCase().includes(mun)) return false;
        return true;
    });

    const header = ["Município","UF","Região","Empreendimento","Modalidade","Executor",
                    "Estágio","Estimativa 2023-2030","% Executado","Porte Populacional","Eixo"];
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

    ["mg-f-eixo","mg-f-modalidade","mg-f-estagio","mg-f-executor",
     "mg-f-regiao","mg-f-uf","mg-f-porte"].forEach(id => {
        document.getElementById(id)?.addEventListener("change", filtrar);
    });
    document.getElementById("mg-f-municipio")?.addEventListener("input", filtrar);
    document.getElementById("mg-btn-limpar")?.addEventListener("click", limparFiltros);
    document.getElementById("mg-btn-print")?.addEventListener("click", imprimirMapa);
    document.getElementById("mg-btn-baixar")?.addEventListener("click", baixarDados);
});
