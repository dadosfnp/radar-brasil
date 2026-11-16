import unicodedata

from django.db.models import Count

from apps.indicadores.models import RegistroParametro

# ── Constantes ────────────────────────────────────────────────────
CORES_NIVEL = {
    "Nível 1": "#e06b6b",
    "Nível 2": "#f09a50",
    "Nível 3": "#e8c53a",
    "Nível 4": "#72be79",
    "Nível 5": "#1a4a35",
}

# eixo_front → eixo normalizado (forma armazenada no banco)
EIXO_MAP = {
    "Governanca": "governanca",
    "Politicas e Planos": "politicas e planos",
    "Programas": "programas",
    "Linhas de Financiamento": "linhas de financiamento",
}

# Nomes usados para ORDENAÇÃO (devem bater com os valores no banco)
ORDEM_CRITERIOS = {
    "Governanca": [
        "Operacionalidade",
        "Espaço de diálogo federativo",
        "Financiamento",
        "Representação de Gênero, Raça e Etnia",
        "Comunicação e Transparência",
    ],
    "Politicas e Planos": [
        "Operacionalidade",
        "Espaço de diálogo federativo",
        "Financiamento",
        "Comunicação e Transparência",
    ],
    "Programas": [
        "Cooperação Federativa",
        "Capilaridade e Alcance Territorial",
        "Financiamento",
        "Fortalecimento da Capacidade Local",
        "Monitoramento e Participação Local",
    ],
    "Linhas de Financiamento": [
        "Desenho Participativo da Linha de Financiamento",
        "Capacidade de Execução Descentralizada",
        "Monitoramento e Prestação de Contas",
    ],
}

# Nomes exibidos nos gráficos (renomeia valores do banco antes de retornar)
_CRITERIO_DISPLAY_PT = {
    "Financiamento": "Sustentabilidade Financeira",
    "Representação de Gênero, Raça e Etnia": "Diversidade e Representatividade",
    "Monitoramento e Participação Local": "Monitoramento e Avaliação",
}
_CRITERIO_DISPLAY_EN = {
    "Financing": "Financial Sustainability",
    "Gender, Race and Ethnicity Representation": "Diversity and Representativeness",
    "Monitoring and Local Participation": "Monitoring and Evaluation",
}

# Nomes de critérios EN → PT, usado APENAS para ordenação via ORDEM_CRITERIOS
_EN_CRITERIO = {
    "Operability": "Operacionalidade",
    "Federative dialogue space": "Espaço de diálogo federativo",
    "Communication and Transparency": "Comunicação e Transparência",
    "Financing": "Financiamento",
    "Gender, Race and Ethnicity Representation": "Representação de Gênero, Raça e Etnia",
    "Federative Cooperation": "Cooperação Federativa",
    "Capillarity and Territorial Reach": "Capilaridade e Alcance Territorial",
    "Strengthening Local Capacity": "Fortalecimento da Capacidade Local",
    "Monitoring and Local Participation": "Monitoramento e Participação Local",
    "Participatory Design of the Financing Line": "Desenho Participativo da Linha de Financiamento",
    "Decentralized Execution Capability": "Capacidade de Execução Descentralizada",
    "Monitoring and Accountability": "Monitoramento e Prestação de Contas",
}

# "Visão Geral" do Painel (2026-11-16): Nível Eixo, peso e descrições de uma linha.
# Nível Eixo/Nível Parcial são sempre media simples (ver texto do Nivel Pais) — peso
# e so um rotulo exibido, nunca entra em nenhuma media.
NIVEL_NUM = {"Nível 1": 1, "Nível 2": 2, "Nível 3": 3, "Nível 4": 4, "Nível 5": 5}

# Renomeia mais 2 criterios de Linhas de Financiamento para nomes curtos (mockup dos
# especialistas) — nomes unicos, sem risco de colidir com outro eixo.
_CRITERIO_DISPLAY_PT["Desenho Participativo da Linha de Financiamento"] = "Desenho Participativo"
_CRITERIO_DISPLAY_PT["Capacidade de Execução Descentralizada"] = "Execução Descentralizada"
_CRITERIO_DISPLAY_EN["Participatory Design of the Financing Line"] = "Participatory Design"
_CRITERIO_DISPLAY_EN["Decentralized Execution Capability"] = "Decentralized Execution"

_DESCRICAO_EIXO_PT = {
    "Governanca": (
        "A governança climática brasileira funciona, mas ainda sem estados e "
        "municípios no centro das decisões."
    ),
    "Politicas e Planos": (
        "Há recursos para elaborar e executar planos com a temática climática. O "
        "que falta, no entanto, é a participação de quem vai executá-los, ou seja, "
        "os estados e municípios."
    ),
    "Programas": (
        "Apesar da baixa participação de estados e municípios na elaboração dos "
        "programas federais, estes têm um alcance territorial satisfatório. Falta "
        "apoio técnico e recursos que cheguem na ponta."
    ),
    "Linhas de Financiamento": (
        "Estados e municípios não participam da estruturação das linhas de "
        "financiamento e acessam pouco os recursos disponíveis."
    ),
}
_DESCRICAO_EIXO_EN = {
    "Governanca": (
        "Brazilian climate governance works, but states and municipalities are "
        "still not at the center of decisions."
    ),
    "Politicas e Planos": (
        "Resources exist to draft and execute plans on the climate agenda. What is "
        "missing is the participation of those who will execute them — the states "
        "and municipalities."
    ),
    "Programas": (
        "Despite the low participation of states and municipalities in designing "
        "federal programs, they have satisfactory territorial reach. Technical "
        "support and funds are not reaching the ground."
    ),
    "Linhas de Financiamento": (
        "States and municipalities do not take part in structuring financing "
        "lines and have little access to the funds available."
    ),
}

# Descricao de 1 linha por criterio, chave = (eixo_front, nome de EXIBICAO). O mesmo
# nome de criterio (ex.: "Operacionalidade") significa algo diferente em cada eixo.
_DESCRICAO_CRITERIO_PT = {
    "Governanca": {
        "Operacionalidade": "Influência e regularidade de funcionamento da instância",
        "Espaço de diálogo federativo": "Representação de União, estados e municípios",
        "Sustentabilidade Financeira": "Recursos para os custos operacionais da instância",
        "Diversidade e Representatividade": "Previsão normativa de gênero, raça e etnia",
        "Comunicação e Transparência": "Informações disponíveis em sites e redes",
    },
    "Politicas e Planos": {
        "Operacionalidade": "Atualização e periodicidade da política ou do plano",
        "Espaço de diálogo federativo": "Participação dos entes na elaboração e na execução",
        "Financiamento": "Especificação das fontes de recursos",
        "Comunicação e Transparência": "Informações públicas sobre a política ou o plano",
    },
    "Programas": {
        "Cooperação Federativa": "Participação dos entes na estruturação do programa",
        "Capilaridade e Alcance Territorial": "Descentralização da execução das ações",
        "Financiamento": "Dotação orçamentária, repasses e fundos",
        "Fortalecimento da Capacidade Local": "Apoio técnico e capacitação dos entes",
        "Monitoramento e Avaliação": "Instrumentos de acompanhamento da execução",
    },
    "Linhas de Financiamento": {
        "Desenho Participativo": "Participação das entidades no desenho das linhas",
        "Execução Descentralizada": "Descentralização dos recursos",
        "Monitoramento e Prestação de Contas": "Grau de participação dos entes no monitoramento",
    },
}
_DESCRICAO_CRITERIO_EN = {
    "Governanca": {
        "Operability": "Influence and regularity of the body's operation",
        "Federative dialogue space": "Representation of the Union, states and municipalities",
        "Financial Sustainability": "Funds for the body's operating costs",
        "Diversity and Representativeness": "Regulatory provision for gender, race and ethnicity",
        "Communication and Transparency": "Information available on websites and social media",
    },
    "Politicas e Planos": {
        "Operability": "Update and periodicity of the policy or plan",
        "Federative dialogue space": "Participation of the entities in drafting and execution",
        "Financing": "Specification of funding sources",
        "Communication and Transparency": "Public information about the policy or plan",
    },
    "Programas": {
        "Federative Cooperation": "Participation of the entities in structuring the program",
        "Capillarity and Territorial Reach": "Decentralization of action execution",
        "Financing": "Budget allocation, transfers and funds",
        "Strengthening Local Capacity": "Technical support and capacity building for the entities",
        "Monitoring and Evaluation": "Instruments for tracking execution",
    },
    "Linhas de Financiamento": {
        "Participatory Design": "Participation of entities in designing the financing lines",
        "Decentralized Execution": "Decentralization of funds",
        "Monitoring and Accountability": "Degree of participation of entities in monitoring",
    },
}

# Peso exibido (rotulo "peso N"). Default 1 (sem badge); so os casos abaixo mostram
# "peso 2". Nunca entra em nenhuma media — Nivel Eixo/Parcial seguem media simples.
_PESO_CRITERIO_PT = {
    "Governanca": {"Espaço de diálogo federativo": 2},
    "Politicas e Planos": {"Operacionalidade": 2},
    "Programas": {"Financiamento": 2},
    "Linhas de Financiamento": {"Execução Descentralizada": 2},
}
_PESO_CRITERIO_EN = {
    "Governanca": {"Federative dialogue space": 2},
    "Politicas e Planos": {"Operability": 2},
    "Programas": {"Financing": 2},
    "Linhas de Financiamento": {"Decentralized Execution": 2},
}


def _normalizar(texto: str) -> str:
    return (
        unicodedata.normalize("NFKD", str(texto))
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
        .strip()
    )


# ── API pública ───────────────────────────────────────────────────


def get_total_municipios(lang: str = "pt") -> int:
    qs = (
        RegistroParametro.objects.filter(lang=lang, nivel__in=CORES_NIVEL.keys())
        .values("eixo", "avaliacao")
        .annotate(n=Count("id"))
    )
    if not qs.exists():
        return 0
    return max(r["n"] for r in qs)


def dados_para_grafico(eixo_front: str, lang: str = "pt") -> dict:
    eixo_norm = EIXO_MAP.get(eixo_front)
    if not eixo_norm:
        return {
            "labels": [],
            "datasets": [],
            "erro": f"Eixo desconhecido: {eixo_front}",
            "nivel_eixo": None,
            "total_componentes": 0,
            "descricao_eixo": "",
            "criterios": [],
        }

    qs = RegistroParametro.objects.filter(lang=lang, eixo=eixo_norm, nivel__in=CORES_NIVEL.keys())
    if not qs.exists():
        return {
            "labels": [],
            "datasets": [],
            "nivel_eixo": None,
            "total_componentes": 0,
            "descricao_eixo": "",
            "criterios": [],
        }

    todas = sorted(qs.values_list("avaliacao", flat=True).distinct())

    # Ordena conforme ORDEM_CRITERIOS
    ordem = ORDEM_CRITERIOS.get(eixo_front, [])
    if ordem:
        ordem_norm = [_normalizar(o) for o in ordem]

        def _sort_key(av):
            av_pt = _EN_CRITERIO.get(av, av) if lang == "en" else av
            try:
                return ordem_norm.index(_normalizar(av_pt))
            except ValueError:
                return len(ordem_norm)

        labels = sorted(todas, key=_sort_key)
    else:
        labels = sorted(todas)

    # Contagem por avaliacao + nivel
    contagem = {}
    for reg in qs.values("avaliacao", "nivel"):
        key = (reg["avaliacao"], reg["nivel"])
        contagem[key] = contagem.get(key, 0) + 1

    datasets = []
    for nivel, cor in CORES_NIVEL.items():
        data = [contagem.get((av, nivel), 0) for av in labels]
        label_display = nivel.replace("Nível ", "Level ") if lang == "en" else nivel
        datasets.append(
            {
                "label": label_display,
                "data": data,
                "backgroundColor": cor,
                "borderWidth": 0,
                "borderRadius": 3,
                "stack": "stack1",
            }
        )

    # Nível médio por critério (antes do rename, "labels" ainda são os valores do
    # banco) e total de componentes avaliados em cada um
    nivel_medio_raw = {}
    total_raw = {}
    for av in labels:
        total = sum(contagem.get((av, n), 0) for n in CORES_NIVEL)
        soma = sum(contagem.get((av, n), 0) * NIVEL_NUM[n] for n in CORES_NIVEL)
        nivel_medio_raw[av] = round(soma / total, 1) if total else 0
        total_raw[av] = total
    labels_raw = list(labels)

    # Aplica nomes de exibição (renomeia labels do banco antes de retornar)
    display_map = _CRITERIO_DISPLAY_EN if lang == "en" else _CRITERIO_DISPLAY_PT
    # "Financiamento" → "Sustentabilidade Financeira" apenas no eixo Governança
    fin_key = "Financing" if lang == "en" else "Financiamento"
    if eixo_front != "Governanca":
        display_map = {k: v for k, v in display_map.items() if k != fin_key}
    labels = [display_map.get(lb, lb) for lb in labels]

    # "Visão Geral": Nível Eixo (média simples dos níveis médios de cada critério —
    # mesma fórmula de 3 etapas documentada no Nível País, sem ponderação), descrição
    # do eixo e, por critério, descrição + peso (so rotulo, nunca entra na média)
    desc_eixo_map = _DESCRICAO_EIXO_EN if lang == "en" else _DESCRICAO_EIXO_PT
    desc_criterio_map = _DESCRICAO_CRITERIO_EN if lang == "en" else _DESCRICAO_CRITERIO_PT
    peso_map = _PESO_CRITERIO_EN if lang == "en" else _PESO_CRITERIO_PT
    desc_criterio_eixo = desc_criterio_map.get(eixo_front, {})
    peso_eixo = peso_map.get(eixo_front, {})

    criterios = []
    for raw, nome in zip(labels_raw, labels):
        criterios.append(
            {
                "nome": nome,
                "descricao": desc_criterio_eixo.get(nome, ""),
                "peso": peso_eixo.get(nome, 1),
                "nivel_medio": nivel_medio_raw[raw],
                "total_componentes": total_raw[raw],
            }
        )

    nivel_eixo = (
        round(sum(c["nivel_medio"] for c in criterios) / len(criterios), 1) if criterios else None
    )
    total_componentes = max(total_raw.values()) if total_raw else 0

    return {
        "labels": labels,
        "datasets": datasets,
        "nivel_eixo": nivel_eixo,
        "total_componentes": total_componentes,
        "descricao_eixo": desc_eixo_map.get(eixo_front, ""),
        "criterios": criterios,
    }
