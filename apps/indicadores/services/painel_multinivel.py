import json
import os
import time
import unicodedata
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ── Configuração ──────────────────────────────────────────────
CREDS_PATH          = ".secrets/fnp-radar-sheets.json"
SHEET_PARAMETROS_ID = "1ewpocM6__tTge6KMK5wuRqv_kfx50bnlp9iA-HmB4O0"
WORKSHEET_NAME      = "dados"
CACHE_TTL           = 1800  # 30 minutos

CORES_NIVEL = {
    "Nível 0": "#bdc5d0",
    "Nível 1": "#e06b6b",
    "Nível 2": "#f09a50",
    "Nível 3": "#e8c53a",
    "Nível 4": "#72be79",
    "Nível 5": "#7aaed4",
}

# O que o front manda → o que buscamos na planilha (sem acento, igual ao R)
EIXO_MAP = {
    "Governanca":             "Governanca",
    "Politicas e Planos":     "Politicas e Planos",
    "Programas":              "Programas",
    "Linhas de Financiamento":"Linhas de Financiamento",
}

# Cache em memória
_cache = {
    "df":        None,
    "timestamp": 0,
}


def _normalizar(texto: str) -> str:
    """Remove acentos e coloca em minúsculas para comparação segura."""
    return (
        unicodedata.normalize("NFKD", texto)
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


def _ler_parametros() -> pd.DataFrame:
    agora = time.time()

    if _cache["df"] is not None and (agora - _cache["timestamp"]) < CACHE_TTL:
        print("[CACHE HIT] Usando dados em memória.")
        return _cache["df"]

    print("[CACHE MISS] Buscando dados do Google Sheets...")
    client = _get_client()
    sh     = client.open_by_key(SHEET_PARAMETROS_ID)
    ws     = sh.worksheet(WORKSHEET_NAME)
    dados  = ws.get_all_records()
    df     = pd.DataFrame(dados)

    _cache["df"]        = df
    _cache["timestamp"] = agora

    # LOG: mostra os valores únicos da coluna Eixo para diagnóstico
    if "Eixo" in df.columns:
        print("[CACHE] Eixos na planilha:", df["Eixo"].unique().tolist())

    print(f"[CACHE] {len(df)} registros. Expira em {CACHE_TTL // 60} min.")
    return df


def get_total_municipios() -> int:
    df = _ler_parametros()
    if df.empty or not {"Eixo", "Avaliação", "Nível"}.issubset(df.columns):
        return 0
    df_valid = df[df["Nível"].isin(CORES_NIVEL.keys())]
    contagem = df_valid.groupby(["Eixo", "Avaliação"]).size()
    return int(contagem.max()) if not contagem.empty else 0


def dados_para_grafico(eixo_front: str) -> dict:
    eixo_busca = EIXO_MAP.get(eixo_front)
    if not eixo_busca:
        return {
            "labels":   [],
            "datasets": [],
            "erro": f"Eixo desconhecido: {eixo_front}",
        }

    df = _ler_parametros()

    # Verifica colunas mínimas
    colunas_esperadas = {"Eixo", "Avaliação", "Nível"}
    if not colunas_esperadas.issubset(set(df.columns)):
        return {
            "labels":   [],
            "datasets": [],
            "erro": f"Colunas encontradas: {list(df.columns)}",
        }

    # Normaliza para comparação sem acento
    df = df.copy()
    df["Eixo_norm"]     = df["Eixo"].astype(str).apply(_normalizar)
    df["Avaliação"]     = df["Avaliação"].astype(str).str.strip()
    df["Nível"]         = df["Nível"].astype(str).str.strip()

    eixo_norm = _normalizar(eixo_busca)

    # Filtra pelo eixo e por níveis válidos
    df_eixo = df[
        (df["Eixo_norm"] == eixo_norm) &
        (df["Nível"].isin(CORES_NIVEL.keys()))
    ].copy()

    print(f"[FILTRO] Eixo '{eixo_front}' → '{eixo_busca}' → norm '{eixo_norm}': {len(df_eixo)} registros")

    if df_eixo.empty:
        return {"labels": [], "datasets": []}

    # Ordena Avaliações pelo score de Nível 5 (igual ao R)
    score = (
        df_eixo[df_eixo["Nível"] == "Nível 5"]
        .groupby("Avaliação")
        .size()
        .reset_index(name="score")
    )
    todas    = df_eixo["Avaliação"].unique().tolist()
    score_df = pd.DataFrame({"Avaliação": todas})
    score_df = score_df.merge(score, on="Avaliação", how="left").fillna(0)
    score_df = score_df.sort_values("score", ascending=True)
    labels   = score_df["Avaliação"].tolist()

    # Contagem por Avaliação + Nível
    contagem = (
        df_eixo.groupby(["Avaliação", "Nível"])
        .size()
        .reset_index(name="qtd")
    )

    # Monta datasets — um por nível
    datasets = []
    for nivel, cor in CORES_NIVEL.items():
        data = []
        for avaliacao in labels:
            filtro = contagem[
                (contagem["Avaliação"] == avaliacao) &
                (contagem["Nível"] == nivel)
            ]
            data.append(int(filtro["qtd"].sum()))

        datasets.append({
            "label":           nivel,
            "data":            data,
            "backgroundColor": cor,
            "borderWidth":     0,
            "borderRadius":    3,
            "stack":           "stack1",
        })

    return {
        "labels":   labels,
        "datasets": datasets,
    }