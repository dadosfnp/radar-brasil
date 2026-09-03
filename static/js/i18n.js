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
            "Todos os Programas":     "All Programs",
            "Todos os Setores":       "All Sectors",
            "Todas as Origens":       "All Sources",
            "Todos os Entes":         "All Entities",
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
            "População":              "Population",
            "Região":                 "Region",

            // ── Mapa — CSV headers ───────────────────────────────
            "UF":                         "State",
            "Empreendimento":             "Project",
            "Modalidade":                 "Modality",
            "Executor":                   "Executor",
            "Estágio":                    "Stage",
            "Estimativa 2023-2030":       "Estimate 2023-2030",
            "% Executado":                "% Executed",
            "Eixo":                       "Axis",

            // ── Financiamento Climático — CSV headers ────────────
            "Programas e Linhas de Financiamento": "Programs and Financing Lines",
            "Valor do Financiamento":              "Financing Value",
            "Contrapartida":                       "Counterpart",
            "Repasse Federal":                     "Federal Transfer",
            "Repasse Estadual":                    "State Transfer",
            "Repasse Municipal":                   "Municipal Transfer",

            // ── Mensagens de estado ──────────────────────────────
            "Carregando...":                        "Loading...",
            "Selecione um item para visualizar a avaliação.": "Select an item to view the assessment.",
            "Falha ao conectar. Verifique sua conexão.": "Connection failed. Check your connection.",
            "Erro ao carregar dados.":              "Error loading data.",
            "Nenhum dado encontrado.":              "No data found.",
            "Não foi possível carregar os dados. Verifique sua conexão e recarregue a página.":
                "Could not load data. Check your connection and reload the page.",
            "Nenhum resultado encontrado":          "No results found",
            "Nenhum resultado":                     "No results",
            "Nenhuma informação disponível.":       "No information available.",
            "Erro ao carregar ficha técnica.":      "Error loading technical sheet.",
            "Ver níveis":                           "View levels",
            "Nível máximo de avaliação":            "Maximum evaluation level",
            "atual":                                "current",
            "Dados não disponíveis para este critério.": "Data not available for this criterion.",
            "Falha ao conectar com o servidor. Verifique sua conexão e recarregue a página.":
                "Failed to connect to the server. Check your connection and reload the page.",
            "Nenhum dado encontrado para esta estrutura.": "No data found for this structure.",
            "Erro ao carregar dados. Verifique sua conexão e tente novamente.":
                "Error loading data. Check your connection and try again.",
            "Sem dados":                            "No data",
            "Nenhum selecionado":                   "None selected",
            "Nenhum":                               "None",
            "selecionado":                          "selected",
            "selecionados":                         "selected",

            // ── Avaliação / Ficha ────────────────────────────────
            "Instância de Governança": "Governance Instance",
            "Setor":                  "Sector",
            "Buscar...":              "Search...",
            "Fechar":                 "Close",
            "RADAR BRASIL – Impulsionando a Ação Climática Federativa":
                "RADAR BRASIL – Driving Federative Climate Action",

            // ── Painel Multinível — critérios renomeados ─────────
            "Sustentabilidade Financeira":       "Financial Sustainability",
            "Diversidade e Representatividade":  "Diversity and Representativeness",

            // ── Painel Multinível (abas) ─────────────────────────
            "Governança":             "Governance",
            "Governanca":             "Governance",
            "Políticas e Planos":     "Policies & Plans",
            "Politicas e Planos":     "Policies & Plans",
            "Programas":              "Programs",
            "Linhas de Financiamento":"Financing Lines",
            "estrutura":              "structure",
            "estruturas":             "structures",

            // ── Labels da API (carregarFiltros) ──────────────────
            "Instância":              "Instance",
            "Setor":                  "Sector",
            "Política / Plano":       "Policy / Plan",
            "Programa":               "Program",
            "Linha de Financiamento": "Financing Line",

            // ── Financiamento – tabela data-label / tooltip ───────
            "Modalidade":             "Modality",
            "Origem":                 "Source",
            "Valor":                  "Value",
            "Estadual":               "State",
            "registros":              "records",

            // ── PDF da ficha técnica ──────────────────────────────
            "Ficha Técnica":          "Technical Sheet",

            // ── Financiamento Climático ──────────────────────────
            "Distribuição por Setor": "Distribution by Sector",
            "Origem dos Recursos":    "Source of Funds",
            "Ente Federativo":        "Federal Entity",

            // ── Totais do mapa ───────────────────────────────────
            "Total Estimado":         "Total Estimate",
            "Para":                   "For",
            "Município":              "Municipality",
            "municípios":             "municipalities",

            // ── Paginação ────────────────────────────────────────
            "Anterior":               "Previous",
            "Próximo":                "Next",
            "de":                     "of",

            // ── Print / Botões ───────────────────────────────────
            "Gerando…":               "Generating…",
            "Print Mapa":             "Print Map",
            "Imprimir Tela":          "Print Page",
            "Baixar Dados":           "Download Data",
            "contribuidores":         "contributors",

            // ── Nota País ────────────────────────────────────────
            "OCEANO PACÍFICO":        "PACIFIC OCEAN",
            "OCEANO ATLÂNTICO":       "ATLANTIC OCEAN",
            "OCEANO ÍNDICO":          "INDIAN OCEAN",
            "Nota":                   "Score",
            "Nota não atribuída":     "Score not assigned",
            "Nível 3,0":              "Level 3.0",
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
