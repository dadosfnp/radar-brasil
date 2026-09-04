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
        return {"labels": [], "datasets": [], "erro": f"Eixo desconhecido: {eixo_front}"}

    qs = RegistroParametro.objects.filter(lang=lang, eixo=eixo_norm, nivel__in=CORES_NIVEL.keys())
    if not qs.exists():
        return {"labels": [], "datasets": []}

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

    # Aplica nomes de exibição (renomeia labels do banco antes de retornar)
    display_map = _CRITERIO_DISPLAY_EN if lang == "en" else _CRITERIO_DISPLAY_PT
    labels = [display_map.get(lb, lb) for lb in labels]

    return {"labels": labels, "datasets": datasets}
