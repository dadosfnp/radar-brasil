import json
import os
import time
import unicodedata
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

CREDS_PATH = ".secrets/fnp-radar-sheets.json"
SHEET_FICHAS_ID = "16s59h5uE0R6GZTkrjQZI152gUOjfjxeOeAwy7v6JYH8"
SHEET_PARAMS_ID = "1jKGDhsjDYHRKEJCLdP-5zCxCSh5q5A5t8x1RhErmEoE"
CACHE_TTL = 1800  # 30 min

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

_cache_fichas = {"df": None, "ts": 0}
_cache_params = {"df": None, "ts": 0}


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


def _ler_sheet(sheet_id: str, worksheet: str, cache: dict) -> pd.DataFrame:
    agora = time.time()
    if cache["df"] is not None and (agora - cache["ts"]) < CACHE_TTL:
        return cache["df"]
    client = _get_client()
    dados = client.open_by_key(sheet_id).worksheet(worksheet).get_all_records()
    df = pd.DataFrame(dados)
    cache["df"] = df
    cache["ts"] = agora
    return df


def _fichas() -> pd.DataFrame:
    return _ler_sheet(SHEET_FICHAS_ID, "dados", _cache_fichas)


def _parametros() -> pd.DataFrame:
    return _ler_sheet(SHEET_PARAMS_ID, "dados", _cache_params)


def get_filtros(eixo_front: str) -> dict:
    eixo_busca = EIXO_MAP.get(eixo_front, eixo_front)
    df = _fichas()

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


def get_tabela(estrutura: str) -> list:
    df = _parametros()
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
        result.append(
            {
                "avaliacao": str(row.get("Avaliação", "")).strip(),
                "criterio": str(row.get("Critério", "")).strip(),
                "descritivo": str(row.get("Descritivo", "")).strip(),
                "nivel": nivel,
                "cor": cor,
            }
        )
    return result


def get_ficha(estrutura: str) -> dict:
    df = _fichas()
    if "Estrutura" not in df.columns:
        return {}

    rows = df[df["Estrutura"].astype(str).str.strip() == estrutura.strip()]
    if rows.empty:
        return {}

    row = rows.iloc[0]

    # (col, label, link_col) — link_col é None quando não há hiperlink
    campos = [
        ("Setor",                    "Setor",                        None),
        ("Descricao",                "Descrição",                    None),
        ("Orgao_responsavel",        "Órgão Responsável",            "Link_orgao"),
        ("Status",                   "Status",                       None),
        ("Arcabouco_normativo",      "Arcabouço Normativo",          "Link_arcabouco"),
        ("Contrapartida",            "Contrapartida",                None),
        ("Espaco_dialogo_federativo","Espaço de Diálogo Federativo", None),
        ("Financiamento",            "Financiamento",                None),
        ("Periodicidade",            "Periodicidade",                None),
        ("Composicao",               "Composição",                   None),
        ("Carater_decisorio",        "Caráter Decisório",            None),
        ("Politica_Plano_relacionado","Política ou Plano Relacionado",None),
        ("Modalidade",               "Modalidade",                   None),
        ("Repasse",                  "Repasse",                      None),
        ("Fontes",                   "Fontes",                       None),
    ]

    _INVALID = {"nan", "Ñ aplica", "N/A", ""}

    def _safe_link(val: str) -> str | None:
        v = str(val).strip()
        return v if v not in _INVALID and v.startswith("http") else None

    resultado = {
        "estrutura": estrutura,
        "campos": [],
        "link_eixo": _safe_link(row.get("Link_eixo", "")),
    }

    for col, label, link_col in campos:
        if col in row.index:
            val = str(row[col]).strip()
            if val and val not in _INVALID:
                campo = {"label": label, "valor": val}
                if link_col and link_col in row.index:
                    campo["url"] = _safe_link(row[link_col])
                resultado["campos"].append(campo)

    return resultado
