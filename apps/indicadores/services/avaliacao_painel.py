import unicodedata

from apps.indicadores.models import RegistroFicha, RegistroParametro

# ── Constantes ────────────────────────────────────────────────────
CORES_NIVEL = {
    "Nível 0": "#E0E0E0",
    "Nível 1": "#F4A6A6",
    "Nível 2": "#F9C89B",
    "Nível 3": "#FFEB99",
    "Nível 4": "#BCD6A2",
    "Nível 5": "#1a4a35",
}

# eixo_front → eixo normalizado (forma armazenada no banco)
EIXO_MAP = {
    "Governanca": "governanca",
    "Politicas e Planos": "politicas e planos",
    "Programas": "programas",
    "Linhas de Financiamento": "linhas de financiamento",
}

LABEL_ESTRUTURA = {
    "Governanca": "Instância de Governança",
    "Politicas e Planos": "Política / Plano",
    "Programas": "Programa",
    "Linhas de Financiamento": "Linha de Financiamento",
}

LABEL_SETOR = {
    "Governanca": "Setor",
    "Politicas e Planos": "Setor",
    "Programas": "Setor",
    "Linhas de Financiamento": "Setor",
}

_CAMPOS_LABELS = {
    "setor": ("Setor", "Sector"),
    "descricao": ("Descrição", "Description"),
    "orgao_responsavel": ("Órgão Responsável", "Responsible Agency"),
    "arcabouco_normativo": ("Arcabouço Normativo", "Regulatory Framework"),
    "contrapartida": ("Contrapartida", "Counterpart"),
    "espaco_dialogo_federativo": ("Espaço de Diálogo Federativo", "Federative Dialogue Space"),
    "financiamento": ("Financiamento", "Financing"),
    "periodicidade": ("Periodicidade", "Periodicity"),
    "composicao": ("Composição", "Composition"),
    "carater_decisorio": ("Caráter Decisório", "Decision Authority"),
    "politica_plano_relacionado": ("Política ou Plano Relacionado", "Related Policy or Plan"),
    "modalidade": ("Modalidade", "Modality"),
    "repasse": ("Repasse", "Transfer"),
    "fontes": ("Fontes", "Sources"),
}

_CAMPOS_ORDER = list(_CAMPOS_LABELS.keys())

_INVALID_PT = {"nan", "Ñ aplica", "N/A", ""}
_INVALID_EN = {"nan", "Does not apply", "N/A", "Not applicable", "N/A - Does not apply", ""}

# Renomeia campo `avaliacao` (critério) para exibição na tabela
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

# Mapeamento: atributo do modelo → coluna de link (quando existir)
_LINK_MAP = {
    "orgao_responsavel": "link_orgao",
    "arcabouco_normativo": "link_arcabouco",
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


def get_filtros(eixo_front: str, lang: str = "pt") -> dict:
    eixo_norm = EIXO_MAP.get(eixo_front)
    label_estrutura = LABEL_ESTRUTURA.get(eixo_front, "Estrutura")
    label_setor = LABEL_SETOR.get(eixo_front, "Setor")

    empty = {
        "setores": [],
        "estruturas_por_setor": {},
        "estruturas": [],
        "label_estrutura": label_estrutura,
        "label_setor": label_setor,
    }

    if not eixo_norm:
        return empty

    registros = list(
        RegistroFicha.objects.filter(lang=lang, eixo=eixo_norm).values("estrutura", "setor")
    )
    if not registros:
        return empty

    todas_estruturas = sorted({r["estrutura"] for r in registros if r["estrutura"]})
    setores = sorted({r["setor"] for r in registros if r["setor"]})

    if setores:
        estruturas_por_setor = {}
        setor_por_estrutura = {}
        for r in registros:
            if r["setor"] and r["estrutura"]:
                estruturas_por_setor.setdefault(r["setor"], set()).add(r["estrutura"])
                setor_por_estrutura[r["estrutura"]] = r["setor"]
        estruturas_por_setor = {s: sorted(es) for s, es in estruturas_por_setor.items()}
    else:
        estruturas_por_setor = {}
        setor_por_estrutura = {}

    return {
        "setores": setores,
        "estruturas_por_setor": estruturas_por_setor,
        "estruturas": todas_estruturas,
        "setor_por_estrutura": setor_por_estrutura,
        "label_estrutura": label_estrutura,
        "label_setor": label_setor,
    }


def get_tabela(estrutura: str, lang: str = "pt") -> list:
    qs = RegistroParametro.objects.filter(lang=lang, estrutura=estrutura.strip())
    if not qs.exists():
        return []

    nivel_ordem = {n: i for i, n in enumerate(reversed(list(CORES_NIVEL.keys())))}
    registros = sorted(list(qs), key=lambda r: nivel_ordem.get(r.nivel, 99))

    display_map = _CRITERIO_DISPLAY_EN if lang == "en" else _CRITERIO_DISPLAY_PT
    result = []
    for reg in registros:
        nivel = reg.nivel
        cor = CORES_NIVEL.get(nivel, "#E0E0E0")
        nivel_display = nivel.replace("Nível ", "Level ") if lang == "en" else nivel
        result.append(
            {
                "avaliacao": display_map.get(reg.avaliacao, reg.avaliacao),
                "criterio": reg.criterio,
                "descritivo": reg.descritivo,
                "nivel": nivel_display,
                "cor": cor,
            }
        )
    return result


def get_ficha(estrutura: str, lang: str = "pt") -> dict:
    qs = RegistroFicha.objects.filter(lang=lang, estrutura=estrutura.strip())
    if not qs.exists():
        return {}
    reg = qs.first()

    invalid = _INVALID_EN if lang == "en" else _INVALID_PT
    label_idx = 1 if lang == "en" else 0

    def _safe_link(val: str):
        v = str(val).strip()
        return v if v not in invalid and v.startswith("http") else None

    resultado = {
        "estrutura": estrutura,
        "campos": [],
        "link_eixo": _safe_link(reg.link_eixo or ""),
    }

    for attr in _CAMPOS_ORDER:
        val = (getattr(reg, attr, "") or "").strip()
        if not val or val in invalid:
            continue
        label = _CAMPOS_LABELS[attr][label_idx]
        campo = {"label": label, "valor": val}
        if attr in _LINK_MAP:
            link_attr = _LINK_MAP[attr]
            campo["url"] = _safe_link(getattr(reg, link_attr, "") or "")
        resultado["campos"].append(campo)

    return resultado
