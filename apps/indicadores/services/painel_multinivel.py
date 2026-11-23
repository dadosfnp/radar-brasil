import math
import unicodedata

from django.db.models import Count

from apps.indicadores.models import NotaCalculada, RegistroParametro

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

# Nomes de exibição dos eixos (cards da Landing/Painel ▸ Visão Geral)
NOME_EIXO_PT = {
    "Governanca": "Governança",
    "Politicas e Planos": "Políticas e Planos",
    "Programas": "Programas",
    "Linhas de Financiamento": "Linhas de Financiamento",
}
NOME_EIXO_EN = {
    "Governanca": "Governance",
    "Politicas e Planos": "Policies and Plans",
    "Programas": "Programs",
    "Linhas de Financiamento": "Financing Lines",
}
NOME_EIXO_ES = {
    "Governanca": "Gobernanza",
    "Politicas e Planos": "Políticas y Planes",
    "Programas": "Programas",
    "Linhas de Financiamento": "Líneas de Financiamiento",
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
    "Representation of Gender, Race and Ethnicity": "Diversity and Representativeness",
    "Monitoring and Local Participation": "Monitoring and Evaluation",
}
_CRITERIO_DISPLAY_ES = {
    "Financiamiento": "Sostenibilidad Financiera",
    "Representación de Género, Raza y Etnia": "Diversidad y Representatividad",
    "Monitoreo y Participación Local": "Monitoreo y Evaluación",
}

# Nomes de critérios EN/ES → PT, usado APENAS para ordenação via ORDEM_CRITERIOS
_EN_CRITERIO = {
    "Operability": "Operacionalidade",
    "Federative dialogue space": "Espaço de diálogo federativo",
    "Communication and Transparency": "Comunicação e Transparência",
    "Financing": "Financiamento",
    "Representation of Gender, Race and Ethnicity": "Representação de Gênero, Raça e Etnia",
    "Federative Cooperation": "Cooperação Federativa",
    "Capillarity and Territorial Reach": "Capilaridade e Alcance Territorial",
    "Strengthening Local Capacity": "Fortalecimento da Capacidade Local",
    "Monitoring and Local Participation": "Monitoramento e Participação Local",
    "Participatory Design of the Financing Line": "Desenho Participativo da Linha de Financiamento",
    "Decentralized Execution Capability": "Capacidade de Execução Descentralizada",
    "Monitoring and Accountability": "Monitoramento e Prestação de Contas",
}
_ES_CRITERIO = {
    "Operatividad": "Operacionalidade",
    "Espacio de diálogo federativo": "Espaço de diálogo federativo",
    "Comunicación y Transparencia": "Comunicação e Transparência",
    "Financiamiento": "Financiamento",
    "Representación de Género, Raza y Etnia": "Representação de Gênero, Raça e Etnia",
    "Cooperación Federativa": "Cooperação Federativa",
    "Capilaridad y Alcance Territorial": "Capilaridade e Alcance Territorial",
    "Fortalecimiento de la Capacidad Local": "Fortalecimento da Capacidade Local",
    "Monitoreo y Participación Local": "Monitoramento e Participação Local",
    "Diseño Participativo de la Línea de Financiamiento": (
        "Desenho Participativo da Linha de Financiamento"
    ),
    "Capacidad de Ejecución Descentralizada": "Capacidade de Execução Descentralizada",
    "Monitoreo y Rendición de Cuentas": "Monitoramento e Prestação de Contas",
}

# "Visão Geral" do Painel (2026-11-16): Nível Eixo, peso e descrições de uma linha.
# Os niveis vem da aba CALCULO da planilha (NotaCalculada, ja ponderados por Fator
# de Relevancia e peso). NIVEL_NUM so serve a reserva de media simples sem o sync.
NIVEL_NUM = {"Nível 1": 1, "Nível 2": 2, "Nível 3": 3, "Nível 4": 4, "Nível 5": 5}

# Renomeia mais 2 criterios de Linhas de Financiamento para nomes curtos (mockup dos
# especialistas) — nomes unicos, sem risco de colidir com outro eixo.
_CRITERIO_DISPLAY_PT["Desenho Participativo da Linha de Financiamento"] = "Desenho Participativo"
_CRITERIO_DISPLAY_PT["Capacidade de Execução Descentralizada"] = "Execução Descentralizada"
_CRITERIO_DISPLAY_EN["Participatory Design of the Financing Line"] = "Participatory Design"
_CRITERIO_DISPLAY_EN["Decentralized Execution Capability"] = "Decentralized Execution"
_CRITERIO_DISPLAY_ES["Diseño Participativo de la Línea de Financiamiento"] = "Diseño Participativo"
_CRITERIO_DISPLAY_ES["Capacidad de Ejecución Descentralizada"] = "Ejecución Descentralizada"

_DESCRICAO_EIXO_PT = {
    "Governanca": (
        "Acompanhe os arranjos institucionais e mecanismos de participação "
        "federativa que estruturam a ação climática multinível."
    ),
    "Politicas e Planos": (
        "Identifique os instrumentos de orientação estratégica existente no "
        "enfrentamento das mudanças climáticas."
    ),
    "Programas": (
        "Identifique as ações e iniciativas planejadas para reduzir impactos "
        "das mudanças climáticas."
    ),
    "Linhas de Financiamento": (
        "Analise os investimentos e transferências interfederativas em apoio "
        "ao enfrentamento das mudanças climáticas."
    ),
}
_DESCRICAO_EIXO_EN = {
    "Governanca": (
        "Track the institutional arrangements and federative participation "
        "mechanisms that structure multilevel climate action."
    ),
    "Politicas e Planos": (
        "Identify the strategic guidance instruments that exist to tackle " "climate change."
    ),
    "Programas": (
        "Identify the actions and initiatives planned to reduce the impacts " "of climate change."
    ),
    "Linhas de Financiamento": (
        "Review the investments and interfederative transfers supporting "
        "the response to climate change."
    ),
}
_DESCRICAO_EIXO_ES = {
    "Governanca": (
        "Siga los arreglos institucionales y los mecanismos de participación "
        "federativa que estructuran la acción climática multinivel."
    ),
    "Politicas e Planos": (
        "Identifique los instrumentos de orientación estratégica existentes "
        "para enfrentar el cambio climático."
    ),
    "Programas": (
        "Identifique las acciones e iniciativas planificadas para reducir "
        "los impactos del cambio climático."
    ),
    "Linhas de Financiamento": (
        "Analice las inversiones y transferencias interfederativas de apoyo "
        "al enfrentamiento del cambio climático."
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
_DESCRICAO_CRITERIO_ES = {
    "Governanca": {
        "Operatividad": "Influencia y regularidad de funcionamiento de la instancia",
        "Espacio de diálogo federativo": "Representación de la Unión, estados y municipios",
        "Sostenibilidad Financiera": "Recursos para los costos operativos de la instancia",
        "Diversidad y Representatividad": "Previsión normativa de género, raza y etnia",
        "Comunicación y Transparencia": "Información disponible en sitios y redes",
    },
    "Politicas e Planos": {
        "Operatividad": "Actualización y periodicidad de la política o del plan",
        "Espacio de diálogo federativo": (
            "Participación de las entidades en la elaboración y ejecución"
        ),
        "Financiamiento": "Especificación de las fuentes de recursos",
        "Comunicación y Transparencia": "Información pública sobre la política o el plan",
    },
    "Programas": {
        "Cooperación Federativa": (
            "Participación de las entidades en la estructuración del programa"
        ),
        "Capilaridad y Alcance Territorial": "Descentralización de la ejecución de las acciones",
        "Financiamiento": "Dotación presupuestaria, transferencias y fondos",
        "Fortalecimiento de la Capacidad Local": "Apoyo técnico y capacitación de las entidades",
        "Monitoreo y Evaluación": "Instrumentos de seguimiento de la ejecución",
    },
    "Linhas de Financiamento": {
        "Diseño Participativo": "Participación de las entidades en el diseño de las líneas",
        "Ejecución Descentralizada": "Descentralización de los recursos",
        "Monitoreo y Rendición de Cuentas": (
            "Grado de participación de las entidades en el monitoreo"
        ),
    },
}

# Peso exibido (rotulo "peso N"). Default 1 (sem badge); so os casos abaixo mostram
# "peso 2". Aqui e so o rotulo: a ponderacao de verdade acontece na aba CALCULO.
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
_PESO_CRITERIO_ES = {
    "Governanca": {"Espacio de diálogo federativo": 2},
    "Politicas e Planos": {"Operatividad": 2},
    "Programas": {"Financiamiento": 2},
    "Linhas de Financiamento": {"Ejecución Descentralizada": 2},
}


def arredondar(x: float) -> int:
    """Igual ao ROUND(x; 0) do Google Sheets: ,5 sobe. O round() do Python manda ,5
    pro par mais proximo (round(2.5) == 2) e divergia da planilha."""
    return math.floor(x + 0.5)


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
            av_pt = {"en": _EN_CRITERIO, "es": _ES_CRITERIO}.get(lang, {}).get(av, av)
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
        if lang == "en":
            label_display = nivel.replace("Nível ", "Level ")
        elif lang == "es":
            label_display = nivel.replace("Nível ", "Nivel ")
        else:
            label_display = nivel
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

    # Nível de cada critério (antes do rename, "labels" ainda são os valores do banco)
    # e total de componentes avaliados em cada um. Fonte oficial: aba CALCULO da
    # planilha (NotaCalculada, ponderada por Fator de Relevância e peso do critério);
    # posicao do critério = sua ordem em ORDEM_CRITERIOS (= C01..C0n da planilha).
    notas = dict(NotaCalculada.objects.filter(eixo=eixo_norm).values_list("posicao", "nota"))
    ordem_norm = [_normalizar(o) for o in ordem]
    dict_pt = {"en": _EN_CRITERIO, "es": _ES_CRITERIO}.get(lang, {})

    def _posicao(av):
        try:
            return ordem_norm.index(_normalizar(dict_pt.get(av, av))) + 1
        except ValueError:
            return None

    nivel_medio_raw = {}
    total_raw = {}
    for av in labels:
        total = sum(contagem.get((av, n), 0) for n in CORES_NIVEL)
        nota = notas.get(_posicao(av))
        if nota is None:
            # ponytail: reserva enquanto o sync da aba CALCULO nao rodou — media
            # simples sem Fr/peso, pode divergir da planilha
            soma = sum(contagem.get((av, n), 0) * NIVEL_NUM[n] for n in CORES_NIVEL)
            nota = soma / total if total else 0
        # Numero redondo na Visao Geral (3/5, nao 2.7/5) — pedido do usuario em 2026-11-20
        nivel_medio_raw[av] = arredondar(nota)
        total_raw[av] = total
    labels_raw = list(labels)

    # Aplica nomes de exibição (renomeia labels do banco antes de retornar)
    display_map = {"en": _CRITERIO_DISPLAY_EN, "es": _CRITERIO_DISPLAY_ES}.get(
        lang, _CRITERIO_DISPLAY_PT
    )
    # "Financiamento" → "Sustentabilidade Financeira" apenas no eixo Governança
    fin_key = {"en": "Financing", "es": "Financiamiento"}.get(lang, "Financiamento")
    if eixo_front != "Governanca":
        display_map = {k: v for k, v in display_map.items() if k != fin_key}
    labels = [display_map.get(lb, lb) for lb in labels]

    # "Visão Geral": Nível Eixo (nota oficial da aba CALCULO), descrição do eixo e,
    # por critério, descrição + peso (rotulo)
    desc_eixo_map = {"en": _DESCRICAO_EIXO_EN, "es": _DESCRICAO_EIXO_ES}.get(
        lang, _DESCRICAO_EIXO_PT
    )
    desc_criterio_map = {"en": _DESCRICAO_CRITERIO_EN, "es": _DESCRICAO_CRITERIO_ES}.get(
        lang, _DESCRICAO_CRITERIO_PT
    )
    peso_map = {"en": _PESO_CRITERIO_EN, "es": _PESO_CRITERIO_ES}.get(lang, _PESO_CRITERIO_PT)
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

    if 0 in notas:
        nivel_eixo = arredondar(notas[0])
    elif criterios:
        nivel_eixo = arredondar(sum(c["nivel_medio"] for c in criterios) / len(criterios))
    else:
        nivel_eixo = None
    total_componentes = max(total_raw.values()) if total_raw else 0

    return {
        "labels": labels,
        "datasets": datasets,
        "nivel_eixo": nivel_eixo,
        "total_componentes": total_componentes,
        "descricao_eixo": desc_eixo_map.get(eixo_front, ""),
        "criterios": criterios,
    }
