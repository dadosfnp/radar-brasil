/* Radar Brasil — i18n JS
   Tradução de strings dinâmicas (dados do Sheets + strings hardcoded no JS).
   Uso: t("string em português") → string no idioma atual.
   O idioma é lido do atributo lang do <html> (definido pelo Django). */

(function (global) {
    const DICT = {
        en: {
            // ── Estágios ────────────────────────────────────────
            "Em Execução":            "In Execution",
            "Em Ação Preparatória":   "In Preparatory Action",
            "Concluído":              "Completed",
            "Concluída":              "Completed",
            "Em Elaboração":          "Under Development",
            "Paralisado":             "Halted",
            "Em Licitação":           "In Bidding",
            "Em Contratação":         "Under Contracting",

            // ── Perfil de Investimento ───────────────────────────
            "Investimento Agrupado":  "Grouped Investment",
            "Investimento Único":     "Single Investment",

            // ── Porte Populacional ───────────────────────────────
            "Capital":                "Capital",
            "Acima de 80mil":         "Above 80k",
            "Abaixo de 80mil":        "Below 80k",
            "Acima 80k":              "Above 80k",
            "Abaixo 80k":             "Below 80k",

            // ── Regiões ──────────────────────────────────────────
            "Norte":                  "North",
            "Nordeste":               "Northeast",
            "Centro-Oeste":           "Midwest",
            "Sudeste":                "Southeast",
            "Sul":                    "South",

            // ── Filtros / Selects ────────────────────────────────
            "Todos":                  "All",
            "Todas":                  "All",
            "Todas as Modalidades":   "All Modalities",
            "Todos os Estágios":      "All Stages",
            "Todos os Executores":    "All Executors",
            "Todas as Regiões":       "All Regions",
            "Todos os Estados":       "All States",
            "Todas as regiões":       "All regions",
            "Américas":               "Americas",
            "Europa":                 "Europe",
            "África":                 "Africa",
            "Ásia":                   "Asia",
            "Oceania":                "Oceania",

            // ── Popup do mapa ────────────────────────────────────
            "Porte Populacional":     "Population Size",
            "Perfil Investimento":    "Investment Profile",
            "Estimativa Total":       "Total Estimate",
            "Sem Financiamento":      "No Financing",
            "programa de investimento":  "investment program",
            "programas de investimento": "investment programs",
            "Financiamento":          "Financing",

            // ── Mensagens de estado ──────────────────────────────
            "Carregando...":                        "Loading...",
            "Selecione um item para visualizar a avaliação.": "Select an item to view the assessment.",
            "Falha ao conectar. Verifique sua conexão.": "Connection failed. Check your connection.",
            "Erro ao carregar dados.":              "Error loading data.",
            "Nenhum dado encontrado.":              "No data found.",
            "Não foi possível carregar os dados. Verifique sua conexão e recarregue a página.":
                "Could not load data. Check your connection and reload the page.",
            "Nenhum resultado encontrado":          "No results found",

            // ── Avaliação / Ficha ────────────────────────────────
            "Instância de Governança": "Governance Instance",
            "Setor":                  "Sector",
            "Buscar...":              "Search...",
            "Fechar":                 "Close",

            // ── Painel Multinível (abas) ─────────────────────────
            "Governança":             "Governance",
            "Governanca":             "Governance",
            "Políticas e Planos":     "Policies & Plans",
            "Politicas e Planos":     "Policies & Plans",
            "Programas":              "Programs",
            "Linhas de Financiamento":"Financing Lines",

            // ── Financiamento Climático ──────────────────────────
            "Distribuição por Setor": "Distribution by Sector",
            "Origem dos Recursos":    "Source of Funds",
            "Ente Federativo":        "Federal Entity",

            // ── Totais do mapa ───────────────────────────────────
            "Total Estimado":         "Total Estimate",
            "Para":                   "For",
            "Município":              "Municipality",
            "municípios":             "municipalities",
        },
    };

    function getLang() {
        return (document.documentElement.lang || "pt-br").toLowerCase().slice(0, 2);
    }

    function t(str) {
        if (!str) return str;
        const lang = getLang();
        if (lang === "pt") return str;
        return (DICT[lang] && DICT[lang][str]) ? DICT[lang][str] : str;
    }

    // Exporta globalmente
    global.RBi18n = { t, getLang };
})(window);
