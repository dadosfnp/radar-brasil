import json
import os
import time
import unicodedata
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

CREDS_PATH = ".secrets/fnp-radar-sheets.json"
CACHE_TTL = 1800  # 30 min

# ── Mapeamento de colunas EN → PT ─────────────────────────────
_EN_COLS = {
    # Colunas comuns (fichas + params)
    "Structure": "Estrutura",
    "Axis": "Eixo",
    "Axis_link": "Link_eixo",
    "Sector": "Setor",
    "Level": "Nível",
    "Criterion": "Critério",
    "Descriptive": "Descritivo",
    "Evaluation": "Avaliação",
    "Classification": "Classificação",
    # Colunas das fichas técnicas (nomes confirmados via diagnóstico)
    "Description": "Descricao",
    "Responsible_agency": "Orgao_responsavel",  # nome real na sheet
    "Responsible_body": "Orgao_responsavel",  # variação alternativa
    "Agency_link": "Link_orgao",  # nome real na sheet
    "Body_link": "Link_orgao",  # variação alternativa
    "Regulatory_framework": "Arcabouco_normativo",  # nome real na sheet
    "Normative_framework": "Arcabouco_normativo",  # variação alternativa
    "Framework_link": "Link_arcabouco",
    "Federative_dialogue_space": "Espaco_dialogo_federativo",
    "Financing": "Financiamento",
    "Periodicity": "Periodicidade",
    "Composition": "Composicao",
    "Decision_authority": "Carater_decisorio",  # nome real na sheet
    "Decision_character": "Carater_decisorio",  # variação alternativa
    "Related_policy_plan": "Politica_Plano_relacionado",
    "Counterpart_funding": "Contrapartida",  # nome real na sheet
    "Counterpart": "Contrapartida",  # variação alternativa
    "Modality": "Modalidade",
    "Transfer": "Repasse",
    "Sources": "Fontes",
}

# ── Sheet IDs por idioma ──────────────────────────────────────
SHEET_FICHAS = {
    "pt": {"id": "16s59h5uE0R6GZTkrjQZI152gUOjfjxeOeAwy7v6JYH8", "gid": None},
    "en": {"id": "1EkaWJ2n391vXukwsNTGj-RMd65S55hADtR24lxRXx9g", "gid": 1400373985},
}
SHEET_PARAMS = {
    "pt": {"id": "1jKGDhsjDYHRKEJCLdP-5zCxCSh5q5A5t8x1RhErmEoE", "gid": None},
    "en": {"id": "1t-ivtzjEbn4qneUZr9vaRwCgq7iGKTmIHUnM0aBp4f8", "gid": 1708988989},
}

CORES_NIVEL = {
    "Nível 0": "#E0E0E0",
    "Nível 1": "#F4A6A6",
    "Nível 2": "#F9C89B",
    "Nível 3": "#FFEB99",
    "Nível 4": "#BCD6A2",
    "Nível 5": "#A5C8ED",
}

EIXO_MAP = {
    "Governanca": "Governanca",
    "Politicas e Planos": "Politicas e Planos",
    "Programas": "Programas",
    "Linhas de Financiamento": "Linhas de Financiamento",
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

# Valores EN → PT para colunas discriminadoras
_EN_EIXO = {
    "Governance": "Governanca",
    "Policies & Plans": "Politicas e Planos",
    "Policies and Plans": "Politicas e Planos",
    "Programs": "Programas",
    "Financing Lines": "Linhas de Financiamento",
    "Financing Line": "Linhas de Financiamento",
}

_cache_fichas = {"pt": {"df": None, "ts": 0}, "en": {"df": None, "ts": 0}}
_cache_params = {"pt": {"df": None, "ts": 0}, "en": {"df": None, "ts": 0}}


def _normalizar(texto: str) -> str:
    return (
        unicodedata.normalize("NFKD", str(texto))
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
        .strip()
    )


def _get_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_json = os.getenv("GOOGLE_SHEETS_CREDS_JSON")
    if creds_json:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, scope)
    return gspread.authorize(creds)


def _ler_sheet(cfg: dict, cache_lang: dict) -> pd.DataFrame:
    agora = time.time()
    if cache_lang["df"] is not None and (agora - cache_lang["ts"]) < CACHE_TTL:
        return cache_lang["df"]
    client = _get_client()
    sh = client.open_by_key(cfg["id"])
    ws = sh.get_worksheet_by_id(cfg["gid"]) if cfg["gid"] else sh.worksheet("dados")
    df = pd.DataFrame(ws.get_all_records())
    if cfg.get("gid"):  # sheet EN — normaliza colunas e valores para PT
        df.rename(columns=_EN_COLS, inplace=True)
        if "Eixo" in df.columns:
            df["Eixo"] = df["Eixo"].replace(_EN_EIXO)
        if "Nível" in df.columns:
            df["Nível"] = df["Nível"].astype(str).str.replace(
                r"^Level\s+(\d+)$", r"Nível \1", regex=True
            )
    cache_lang["df"] = df
    cache_lang["ts"] = agora
    return df


def _fichas(lang: str = "pt") -> pd.DataFrame:
    return _ler_sheet(SHEET_FICHAS[lang], _cache_fichas[lang])


def _parametros(lang: str = "pt") -> pd.DataFrame:
    return _ler_sheet(SHEET_PARAMS[lang], _cache_params[lang])


def get_filtros(eixo_front: str, lang: str = "pt") -> dict:
    eixo_busca = EIXO_MAP.get(eixo_front, eixo_front)
    df = _fichas(lang)

    label_estrutura = LABEL_ESTRUTURA.get(eixo_front, "Estrutura")
    label_setor = LABEL_SETOR.get(eixo_front, "Setor")

    if "Eixo" not in df.columns:
        return {
            "setores": [],
            "estruturas_por_setor": {},
            "estruturas": [],
            "label_estrutura": label_estrutura,
            "label_setor": label_setor,
        }

    df["Eixo_norm"] = df["Eixo"].astype(str).apply(_normalizar)
    eixo_norm = _normalizar(eixo_busca)
    df_eixo = df[df["Eixo_norm"] == eixo_norm].copy()

    tem_setor = (
        "Setor" in df.columns
        and df_eixo["Setor"].notna().any()
        and df_eixo["Setor"].astype(str).str.strip().ne("").any()
    )

    todas_estruturas = sorted(
        [e for e in df_eixo["Estrutura"].astype(str).str.strip().unique() if e and e != "nan"]
    )

    if tem_setor:
        df_eixo["Setor"] = df_eixo["Setor"].astype(str).str.strip()
        df_eixo["Estrutura"] = df_eixo["Estrutura"].astype(str).str.strip()

        setores = sorted([s for s in df_eixo["Setor"].unique() if s not in ("", "nan")])
        estruturas_por_setor = {
            s: sorted(df_eixo[df_eixo["Setor"] == s]["Estrutura"].unique().tolist())
            for s in setores
        }
        setor_por_estrutura = {
            str(r["Estrutura"]).strip(): str(r["Setor"]).strip()
            for _, r in df_eixo.iterrows()
            if str(r.get("Estrutura", "")).strip() not in ("", "nan")
            and str(r.get("Setor", "")).strip() not in ("", "nan")
        }
    else:
        setores = []
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
    df = _parametros(lang)
    if "Estrutura" not in df.columns:
        return []

    df_est = df[df["Estrutura"].astype(str).str.strip() == estrutura.strip()].copy()
    if df_est.empty:
        return []

    df_est["Nível"] = df_est["Nível"].astype(str).str.strip()

    nivel_ordem = {n: i for i, n in enumerate(reversed(list(CORES_NIVEL.keys())))}
    df_est["_ord"] = df_est["Nível"].map(nivel_ordem).fillna(99)
    df_est = df_est.sort_values("_ord")

    result = []
    for _, row in df_est.iterrows():
        nivel = row["Nível"]
        cor = CORES_NIVEL.get(nivel, "#E0E0E0")
        nivel_display = nivel.replace("Nível ", "Level ") if lang == "en" else nivel
        result.append(
            {
                "avaliacao": str(row.get("Avaliação", "")).strip(),
                "criterio": str(row.get("Critério", "")).strip(),
                "descritivo": str(row.get("Descritivo", "")).strip(),
                "nivel": nivel_display,
                "cor": cor,
            }
        )
    return result


_CAMPOS_LABELS = {
    # (col_interna): (label_pt, label_en)
    "Setor": ("Setor", "Sector"),
    "Descricao": ("Descrição", "Description"),
    "Orgao_responsavel": ("Órgão Responsável", "Responsible Agency"),
    "Status": ("Status", "Status"),
    "Arcabouco_normativo": ("Arcabouço Normativo", "Regulatory Framework"),
    "Contrapartida": ("Contrapartida", "Counterpart"),
    "Espaco_dialogo_federativo": ("Espaço de Diálogo Federativo", "Federative Dialogue Space"),
    "Financiamento": ("Financiamento", "Financing"),
    "Periodicidade": ("Periodicidade", "Periodicity"),
    "Composicao": ("Composição", "Composition"),
    "Carater_decisorio": ("Caráter Decisório", "Decision Authority"),
    "Politica_Plano_relacionado": ("Política ou Plano Relacionado", "Related Policy or Plan"),
    "Modalidade": ("Modalidade", "Modality"),
    "Repasse": ("Repasse", "Transfer"),
    "Fontes": ("Fontes", "Sources"),
}

_CAMPOS_ORDER = list(_CAMPOS_LABELS.keys())

_INVALID_PT = {"nan", "Ñ aplica", "N/A", ""}
_INVALID_EN = {"nan", "Does not apply", "N/A", "Not applicable", "N/A - Does not apply", ""}


def get_ficha(estrutura: str, lang: str = "pt") -> dict:
    df = _fichas(lang)
    if "Estrutura" not in df.columns:
        return {}

    rows = df[df["Estrutura"].astype(str).str.strip() == estrutura.strip()]
    if rows.empty:
        return {}

    row = rows.iloc[0]
    invalid = _INVALID_EN if lang == "en" else _INVALID_PT
    label_idx = 1 if lang == "en" else 0

    def _safe_link(val: str) -> str | None:
        v = str(val).strip()
        return v if v not in invalid and v.startswith("http") else None

    resultado = {
        "estrutura": estrutura,
        "campos": [],
        "link_eixo": _safe_link(row.get("Link_eixo", "")),
    }

    link_map = {
        "Orgao_responsavel": "Link_orgao",
        "Arcabouco_normativo": "Link_arcabouco",
    }

    for col in _CAMPOS_ORDER:
        if col not in row.index:
            continue
        val = str(row[col]).strip()
        if not val or val in invalid:
            continue
        label = _CAMPOS_LABELS[col][label_idx]
        campo = {"label": label, "valor": val}
        link_col = link_map.get(col)
        if link_col and link_col in row.index:
            campo["url"] = _safe_link(row[link_col])
        resultado["campos"].append(campo)

    return resultado
