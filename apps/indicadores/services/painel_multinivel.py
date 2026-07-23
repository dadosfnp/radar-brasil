import json
import logging
import os
import time
import unicodedata
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)

# ── Configuração ──────────────────────────────────────────────
CREDS_PATH = ".secrets/fnp-radar-sheets.json"
CACHE_TTL = 1800  # 30 minutos

# ── Mapeamento de colunas EN → PT ─────────────────────────────
_EN_COLS = {
    "Structure":    "Estrutura",
    "Axis":         "Eixo",
    "Axis_link":    "Link_eixo",
    "Sector":       "Setor",
    "Level":        "Nível",
    "Criterion":    "Critério",
    "Descriptive":  "Descritivo",
    "Evaluation":   "Avaliação",
    "Classification": "Classificação",
}

SHEET_PARAMETROS = {
    "pt": {"id": "1jKGDhsjDYHRKEJCLdP-5zCxCSh5q5A5t8x1RhErmEoE", "gid": None},
    "en": {"id": "1t-ivtzjEbn4qneUZr9vaRwCgq7iGKTmIHUnM0aBp4f8", "gid": 1708988989},
}

CORES_NIVEL = {
    "Nível 1": "#e06b6b",
    "Nível 2": "#f09a50",
    "Nível 3": "#e8c53a",
    "Nível 4": "#72be79",
    "Nível 5": "#7aaed4",
}

# Ordem de exibição dos critérios (label[0] = topo do gráfico)
ORDEM_CRITERIOS = {
    "Governanca": [
        "Operacionalidade",
        "Espaço de diálogo federativo",
        "Sustentabilidade Financeira",
        "Diversidade e Representatividade",
        "Comunicação e Transparência",
    ],
    "Politicas e Planos": [
        "Operacionalidade",
        "Espaço de diálogo federativo",
        "Sustentabilidade Financeira",
        "Comunicação e Transparência",
    ],
    "Programas": [
        "Cooperação Federativa",
        "Capilaridade e Alcance Territorial",
        "Fortalecimento da Capacidade Local",
        "Monitoramento e Participação Local",
        "Sustentabilidade Financeira",
    ],
    "Linhas de Financiamento": [
        "Desenho Participativo da Linha de Financiamento",
        "Capacidade de Execução Descentralizada",
        "Monitoramento e Prestação de Contas",
    ],
}

# O que o front manda → o que buscamos na planilha (sem acento, igual ao R)
EIXO_MAP = {
    "Governanca": "Governanca",
    "Politicas e Planos": "Politicas e Planos",
    "Programas": "Programas",
    "Linhas de Financiamento": "Linhas de Financiamento",
}

# Cache em memória por idioma
_cache = {
    "pt": {"df": None, "timestamp": 0},
    "en": {"df": None, "timestamp": 0},
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


def _ler_parametros(lang: str = "pt") -> pd.DataFrame:
    agora = time.time()
    c = _cache[lang]

    if c["df"] is not None and (agora - c["timestamp"]) < CACHE_TTL:
        logger.info("painel_multinivel[%s]: cache hit", lang)
        return c["df"]

    logger.info("painel_multinivel[%s]: cache miss — buscando Google Sheets", lang)
    cfg = SHEET_PARAMETROS[lang]
    client = _get_client()
    sh = client.open_by_key(cfg["id"])
    ws = sh.get_worksheet_by_id(cfg["gid"]) if cfg["gid"] else sh.worksheet("dados")
    df = pd.DataFrame(ws.get_all_records())
    if cfg.get("gid"):  # sheet EN — normaliza colunas para PT
        df.rename(columns=_EN_COLS, inplace=True)

    c["df"] = df
    c["timestamp"] = agora

    if "Eixo" in df.columns:
        logger.debug("painel_multinivel[%s]: eixos=%s", lang, df["Eixo"].unique().tolist())

    logger.info("painel_multinivel[%s]: %d registros, expira em %d min", lang, len(df), CACHE_TTL // 60)
    return df


def get_total_municipios(lang: str = "pt") -> int:
    df = _ler_parametros(lang)
    if df.empty or not {"Eixo", "Avaliação", "Nível"}.issubset(df.columns):
        return 0
    df_valid = df[df["Nível"].isin(CORES_NIVEL.keys())]
    contagem = df_valid.groupby(["Eixo", "Avaliação"]).size()
    return int(contagem.max()) if not contagem.empty else 0


def dados_para_grafico(eixo_front: str, lang: str = "pt") -> dict:
    eixo_busca = EIXO_MAP.get(eixo_front)
    if not eixo_busca:
        return {
            "labels": [],
            "datasets": [],
            "erro": f"Eixo desconhecido: {eixo_front}",
        }

    df = _ler_parametros(lang)

    # Verifica colunas mínimas
    colunas_esperadas = {"Eixo", "Avaliação", "Nível"}
    if not colunas_esperadas.issubset(set(df.columns)):
        return {
            "labels": [],
            "datasets": [],
            "erro": f"Colunas encontradas: {list(df.columns)}",
        }

    # Normaliza para comparação sem acento
    df = df.copy()
    df["Eixo_norm"] = df["Eixo"].astype(str).apply(_normalizar)
    df["Avaliação"] = df["Avaliação"].astype(str).str.strip()
    df["Nível"] = df["Nível"].astype(str).str.strip()

    eixo_norm = _normalizar(eixo_busca)

    # Filtra pelo eixo e por níveis válidos
    df_eixo = df[(df["Eixo_norm"] == eixo_norm) & (df["Nível"].isin(CORES_NIVEL.keys()))].copy()

    if df_eixo.empty:
        return {"labels": [], "datasets": []}

    todas = df_eixo["Avaliação"].unique().tolist()

    # Ordena conforme a sequência definida por eixo
    ordem = ORDEM_CRITERIOS.get(eixo_front, [])
    if ordem:
        ordem_norm = [_normalizar(o) for o in ordem]

        def _sort_key(av):
            try:
                return ordem_norm.index(_normalizar(av))
            except ValueError:
                return len(ordem_norm)

        labels = sorted(todas, key=_sort_key)
    else:
        labels = sorted(todas)

    # Contagem por Avaliação + Nível
    contagem = df_eixo.groupby(["Avaliação", "Nível"]).size().reset_index(name="qtd")

    # Monta datasets — um por nível
    datasets = []
    for nivel, cor in CORES_NIVEL.items():
        data = []
        for avaliacao in labels:
            filtro = contagem[(contagem["Avaliação"] == avaliacao) & (contagem["Nível"] == nivel)]
            data.append(int(filtro["qtd"].sum()))

        datasets.append(
            {
                "label": nivel,
                "data": data,
                "backgroundColor": cor,
                "borderWidth": 0,
                "borderRadius": 3,
                "stack": "stack1",
            }
        )

    return {
        "labels": labels,
        "datasets": datasets,
    }
