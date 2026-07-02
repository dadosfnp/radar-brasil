import json
import os
import re
import time
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

CREDS_PATH = ".secrets/fnp-radar-sheets.json"
SHEET_ID = "1lrT6g8JvB3wVZnlVK1JziffzW1mfSYSrGyOqsPZZJG4"
SHEET_GID = 992060842
CACHE_TTL = 1800

_cache = {"df": None, "ts": 0}

CHART_COLORS = [
    "#2c7873",
    "#1a3d4d",
    "#6fb3b8",
    "#f4a261",
    "#e76f51",
    "#52b788",
    "#90e0ef",
    "#ffd166",
    "#ef476f",
    "#118ab2",
]


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


def _ler_sheet() -> pd.DataFrame:
    agora = time.time()
    if _cache["df"] is not None and (agora - _cache["ts"]) < CACHE_TTL:
        return _cache["df"]
    client = _get_client()
    ws = client.open_by_key(SHEET_ID).get_worksheet_by_id(SHEET_GID)
    dados = ws.get_all_records()
    df = pd.DataFrame(dados)
    df.columns = [str(c).strip() for c in df.columns]
    _cache["df"] = df
    _cache["ts"] = agora
    return df


def _col(df, *names):
    for n in names:
        if n in df.columns:
            return n
    return None


def _limpar(v):
    s = str(v).strip()
    return "" if s in ("nan", "None", "N/A") else s


def _uniq(df, col):
    if not col or col not in df.columns:
        return []
    return sorted({_limpar(v) for v in df[col] if _limpar(v) and not _limpar(v).isdigit()})


def _parse_num(v):
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s or s in ("nan", "None", "N/A", "-"):
        return 0.0
    # Remove year prefix like "2025 - " and currency symbols
    s = re.sub(r"^\d{4}\s*[-–]\s*", "", s)
    s = s.replace("R$", "").replace("R $", "").strip()
    # Convert Brazilian format: 10.883.396.000,00 → 10883396000.00
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(".", "")
    nums = re.findall(r"[\d]+\.?[\d]*", s)
    try:
        return float(nums[0]) if nums else 0.0
    except (ValueError, IndexError):
        return 0.0


def _fmt_brl(v):
    if v == 0:
        return "—"
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:.1f} MI"
    if v >= 1_000:
        return f"R$ {v/1_000:.1f} MIL"
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _split_multi(val_str: str) -> list:
    """Converte string com múltiplos valores separados por vírgula em lista."""
    if not val_str:
        return []
    return [v.strip() for v in val_str.split(",") if v.strip()]


def _aplicar_filtros(df: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    prog_col = _col(df, "Programas e Linhas de Financiamento", "Programa", "Programas")
    setor_col = _col(df, "Setor")
    mod_col = _col(df, "Modalidade")
    orig_col = _col(df, "Origem dos Recursos", "Origem")
    ente_col = _col(df, "Ente", "Ente Federado")

    def _filtrar(col, val_str):
        nonlocal df
        vals = _split_multi(val_str)
        if col and vals:
            df = df[df[col].apply(_limpar).isin(vals)]

    _filtrar(prog_col, filtros.get("programa", ""))
    _filtrar(setor_col, filtros.get("setor", ""))
    _filtrar(mod_col, filtros.get("modalidade", ""))
    _filtrar(orig_col, filtros.get("origem", ""))
    _filtrar(ente_col, filtros.get("ente", ""))
    return df


# ── Pública: filtros disponíveis ───────────────────────────────
def get_filtros() -> dict:
    df = _ler_sheet()
    prog_col = _col(df, "Programas e Linhas de Financiamento", "Programa", "Programas")
    setor_col = _col(df, "Setor")
    mod_col = _col(df, "Modalidade")
    orig_col = _col(df, "Origem dos Recursos", "Origem")
    ente_col = _col(df, "Ente", "Ente Federado")
    return {
        "programas": _uniq(df, prog_col),
        "setores": _uniq(df, setor_col),
        "modalidades": _uniq(df, mod_col),
        "origens": _uniq(df, orig_col),
        "entes": _uniq(df, ente_col),
    }


# ── Pública: dados da tabela ───────────────────────────────────
def get_tabela(filtros: dict) -> list:
    df = _ler_sheet()
    df = _aplicar_filtros(df, filtros)

    prog_col = _col(df, "Programas e Linhas de Financiamento", "Programa", "Programas")
    setor_col = _col(df, "Setor")
    mod_col = _col(df, "Modalidade")
    orig_col = _col(df, "Origem dos Recursos", "Origem")
    val_col = _col(df, "Valor de Financiamento", "Valor de financiamento", "Valor do Financiamento")
    cpart_col = _col(df, "Contrapartida", "Contrapatida mínima", "Contrapartida mínima")
    fed_col = _col(df, "Federal", "Repasse Federal")
    est_col = _col(df, "Estadual", "Repasse Estadual")
    mun_col = _col(df, "Municipal", "Repasse Municipal")

    rows = []
    for _, row in df.iterrows():
        rows.append(
            {
                "programa": _limpar(row.get(prog_col, "") if prog_col else ""),
                "setor": _limpar(row.get(setor_col, "") if setor_col else ""),
                "modalidade": _limpar(row.get(mod_col, "") if mod_col else ""),
                "origem": _limpar(row.get(orig_col, "") if orig_col else ""),
                "valor": _limpar(row.get(val_col, "") if val_col else ""),
                "contrapartida": _limpar(row.get(cpart_col, "") if cpart_col else ""),
                "federal": _limpar(row.get(fed_col, "") if fed_col else ""),
                "estadual": _limpar(row.get(est_col, "") if est_col else ""),
                "municipal": _limpar(row.get(mun_col, "") if mun_col else ""),
            }
        )
    return rows


# ── Pública: dados dos gráficos ────────────────────────────────
def get_graficos(filtros: dict) -> dict:
    df = _ler_sheet()
    df = _aplicar_filtros(df, filtros)

    setor_col = _col(df, "Setor")
    orig_col = _col(df, "Origem dos Recursos", "Origem")
    val_col = _col(df, "Valor de Financiamento", "Valor de financiamento", "Valor do Financiamento")
    fed_col = _col(df, "Federal", "Repasse Federal")
    est_col = _col(df, "Estadual", "Repasse Estadual")
    mun_col = _col(df, "Municipal", "Repasse Municipal")

    # ── Gráfico 1: Valor do Financiamento por Setor ────────────
    setor_data = {"labels": [], "values": [], "texts": []}
    if setor_col:
        if val_col:
            df["_val"] = df[val_col].apply(_parse_num)
            g = df.groupby(setor_col)["_val"].sum().reset_index()
            g.columns = ["setor", "total"]
        else:
            g = df.groupby(setor_col).size().reset_index(name="total")
            g.columns = ["setor", "total"]
        g = g[g["setor"].apply(lambda x: bool(_limpar(x)))]
        g = g.sort_values("total", ascending=True)
        setor_data = {
            "labels": g["setor"].tolist(),
            "values": [round(v, 2) for v in g["total"].tolist()],
            "texts": [_fmt_brl(v) for v in g["total"].tolist()],
        }

    # ── Gráfico 2: Origem dos Recursos (donut) ─────────────────
    origem_data = {"labels": [], "values": [], "colors": []}
    if orig_col:
        g = df[df[orig_col].apply(_limpar) != ""].copy()
        g = g.groupby(orig_col).size().reset_index(name="count")
        g.columns = ["origem", "count"]
        g = g.sort_values("count", ascending=False)
        labels = g["origem"].tolist()
        origem_data = {
            "labels": labels,
            "values": g["count"].tolist(),
            "colors": CHART_COLORS[: len(labels)],
        }

    # ── Gráfico 3: Repasse por Ente Federado (pizza) ──────────────────
    def _sum_col(col):
        if not col or col not in df.columns:
            return 0.0
        return float(df[col].apply(_parse_num).sum())

    fed_v = _sum_col(fed_col)
    est_v = _sum_col(est_col)
    mun_v = _sum_col(mun_col)

    ente_data = {
        "labels": ["Federal", "Estadual", "Municipal"],
        "values": [round(fed_v, 2), round(est_v, 2), round(mun_v, 2)],
        "texts": [_fmt_brl(fed_v), _fmt_brl(est_v), _fmt_brl(mun_v)],
    }

    return {
        "setor": setor_data,
        "origem": origem_data,
        "ente": ente_data,
    }
