"""
Leitor de Google Sheets — uso exclusivo do comando sync_sheets_db.
Centraliza o acesso via gspread para importação de dados para o PostgreSQL.
Os services de indicadores NÃO importam este módulo; eles leem direto do banco.
"""

import json
import os
import re
import unicodedata

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

CREDS_PATH = ".secrets/fnp-radar-sheets.json"

# ── IDs das planilhas ────────────────────────────────────────────
SHEET_IDS = {
    # Fichas e Parametros PT passaram a viver na mesma planilha combinada
    # "V01_BANCO DE DADOS_2025" (e-mail Paulo Diego, 2026-11-17), guias
    # "Saida_fichas" e "Saida_parametros" — EN continua nas planilhas
    # separadas de sempre.
    "fichas": {
        "pt": {"id": "10bQF-i3AzELKGFBgWNqRgdC6aLUbekNpg4Rl5kPX2Ic", "gid": None},
        "en": {"id": "1EkaWJ2n391vXukwsNTGj-RMd65S55hADtR24lxRXx9g", "gid": 1400373985},
    },
    "parametros": {
        "pt": {"id": "10bQF-i3AzELKGFBgWNqRgdC6aLUbekNpg4Rl5kPX2Ic", "gid": None},
        "en": {"id": "1t-ivtzjEbn4qneUZr9vaRwCgq7iGKTmIHUnM0aBp4f8", "gid": 1708988989},
    },
    # Financiamento Climático PT passou a viver tambem na planilha combinada V01
    # (aba "Financiamento_climatico", e-mail Paulo Diego, achado em 2026-11-18) —
    # EN/ES agora sao gerados por traducao automatica a partir do PT, mesmo padrao
    # de Fichas/Parametros. A entrada "en" abaixo fica so de historico/referencia,
    # sem uso (igual ja acontecia com fichas/parametros.en).
    "financiamento": {
        "pt": {"id": "10bQF-i3AzELKGFBgWNqRgdC6aLUbekNpg4Rl5kPX2Ic", "gid": None},
        "en": {"id": "1bQoDf4AEElaNy6_vUQSh-tOoZDKZA-R7mEn2eUmZEmk", "gid": 449650871},
    },
    "mapa": {
        "pt": {"id": "1qMPAIB5e6IoG_cdCpBMIgzG8fZS1wUZ1zQbOFW3jACs", "gid": 1619423236},
        "en": {"id": "1uj_8PdAvTScqxSGi0ujBCRhiuJgXXFeaZFO8B4qJtqk", "gid": None},
    },
}

# ── Mapeamentos EN → PT ──────────────────────────────────────────
_EN_COLS_FICHAS_PARAMS = {
    "Structure": "Estrutura",
    "Axis": "Eixo",
    "Axis_link": "Link_eixo",
    "Sector": "Setor",
    "Level": "Nível",
    "Criterion": "Critério",
    "Descriptive": "Descritivo",
    "Evaluation": "Avaliação",
    "Classification": "Classificação",
    "Description": "Descricao",
    "Responsible_agency": "Orgao_responsavel",
    "Responsible_body": "Orgao_responsavel",
    "Agency_link": "Link_orgao",
    "Body_link": "Link_orgao",
    "Regulatory_framework": "Arcabouco_normativo",
    "Normative_framework": "Arcabouco_normativo",
    "Framework_link": "Link_arcabouco",
    "Federative_dialogue_space": "Espaco_dialogo_federativo",
    "Financing": "Financiamento",
    "Periodicity": "Periodicidade",
    "Composition": "Composicao",
    "Decision_authority": "Carater_decisorio",
    "Decision_character": "Carater_decisorio",
    "Related_policy_plan": "Politica_Plano_relacionado",
    "Counterpart_funding": "Contrapartida",
    "Counterpart": "Contrapartida",
    "Modality": "Modalidade",
    "Transfer": "Repasse",
    "Sources": "Fontes",
}

_EN_COLS_FINANCIAMENTO = {
    "Programs_and_funding_lines": "Programas e Linhas de Financiamento",
    "Programs and Financing Lines": "Programas e Linhas de Financiamento",
    "Program": "Programas e Linhas de Financiamento",
    "Programs": "Programas e Linhas de Financiamento",
    "Resource_origin": "Origem dos Recursos",
    "Source of Funds": "Origem dos Recursos",
    "Sources of Funds": "Origem dos Recursos",
    "Resource Origin": "Origem dos Recursos",
    "Origin": "Origem dos Recursos",
    "Funding_amount": "Valor de Financiamento",
    "Financing Value": "Valor de Financiamento",
    "Financing Amount": "Valor de Financiamento",
    "Minimum_counterpart": "Contrapartida",
    "Counterpart": "Contrapartida",
    "Transfer_funding_type": "Ente",
    "Entity": "Ente",
    "Federal Entity": "Ente",
    "Sector": "Setor",
    "Modality": "Modalidade",
    "State": "Estadual",
}

_EN_COLS_MAPA = {
    "Municipality": "Municípios",
    "Municipalities": "Municípios",
    "Axis": "Eixo",
    "Stage": "Estágio",
    "Profile": "Perfil",
    "Estimate_2023_2030": "Estimativa_2023_2030",
    "Population": "Populacao",
    "Enterprise": "Empreendimento",
    "Project": "Empreendimento",
    "Type_of_Executor": "Tipo de Executor",
    "Executor_Type": "Tipo de Executor",
    "Percentage_executed": "Percentual_executado",
    "Modality": "Modalidade",
}

_EN_EIXO = {
    "Governance": "Governanca",
    "Policies & Plans": "Politicas e Planos",
    "Policies and Plans": "Politicas e Planos",
    "Programs": "Programas",
    "Financing Lines": "Linhas de Financiamento",
    "Financing Line": "Linhas de Financiamento",
}


# Como cada byte de continuacao UTF-8 (0x80-0xBF) aparece quando o texto e lido
# como Latin-1 (controles C1 e \xa0-\xbf) ou como cp1252 (aspas curvas, travessoes etc.)
_CONT = (
    "\u0080-\u00bf\u0152\u0153\u0160\u0161\u0178\u017d\u017e\u0192\u02c6\u02dc"
    "\u2013\u2014\u2018-\u201a\u201c-\u201e\u2020-\u2022\u2026\u2030\u2039\u203a"
    "\u20ac\u2122"
)
# Byte inicial de 2, 3 ou 4 bytes seguido do numero certo de continuacoes
_MOJIBAKE_RE = re.compile(
    "[\u00c2-\u00df][" + _CONT + "]"
    "|[\u00e0-\u00ef][" + _CONT + "]{2}"
    "|[\u00f0-\u00f4][" + _CONT + "]{3}"
)


def _bytes_do_trecho(trecho: str) -> bytes:
    return b"".join(c.encode("latin-1") if ord(c) < 256 else c.encode("cp1252") for c in trecho)


def _corrigir_trecho(m):
    try:
        return _bytes_do_trecho(m.group(0)).decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return m.group(0)


def _corrigir_mojibake(valor):
    """Corrige texto colado nas planilhas com encoding errado (UTF-8 lido como
    Latin-1/cp1252: "S\u00e3o" virou "S\u00c3\u00a3o", "\u2013" virou "\u00e2\u20ac\u201c").
    Corrige trecho a trecho, so onde a sequencia forma um caractere UTF-8 valido:
    acento legitimo ("C\u00e2mara", "PAVIMENTA\u00c7\u00c3O") nunca e alterado, mesmo na
    mesma celula de um trecho corrompido. Tambem remove o espaco invisivel (U+200B)
    que vem junto de textos copiados."""
    if not isinstance(valor, str):
        return valor
    return _MOJIBAKE_RE.sub(_corrigir_trecho, valor).replace("\u200b", "")


def _corrigir_mojibake_df(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica _corrigir_mojibake em todas as celulas de texto do DataFrame."""
    return df.map(_corrigir_mojibake)


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


def _ler(cfg: dict, worksheet_name: str = "dados") -> pd.DataFrame:
    client = _get_client()
    sh = client.open_by_key(cfg["id"])
    ws = sh.get_worksheet_by_id(cfg["gid"]) if cfg["gid"] else sh.worksheet(worksheet_name)
    dados = ws.get_all_records()
    df = pd.DataFrame(dados)
    df.columns = [str(col).strip() for col in df.columns]
    return _corrigir_mojibake_df(df)


def ler_fichas(lang: str) -> pd.DataFrame:
    """Lê a sheet Fichas e normaliza colunas + eixo para forma canônica PT."""
    cfg = SHEET_IDS["fichas"][lang]
    df = _ler(cfg, worksheet_name="Saida_fichas" if lang == "pt" else "dados")
    if lang == "en":
        df.rename(columns=_EN_COLS_FICHAS_PARAMS, inplace=True)
        if "Eixo" in df.columns:
            df["Eixo"] = df["Eixo"].replace(_EN_EIXO)
    # Normaliza eixo para forma sem acento/lowercase (chave do DB)
    if "Eixo" in df.columns:
        df["Eixo"] = df["Eixo"].astype(str).apply(_normalizar)
    if lang == "en" and "Nível" in df.columns:
        df["Nível"] = (
            df["Nível"].astype(str).str.replace(r"^Level\s+(\d+)$", r"Nível \1", regex=True)
        )
    return df


def ler_parametros(lang: str) -> pd.DataFrame:
    """Lê a sheet Parâmetros e normaliza colunas + eixo + nível para forma canônica PT."""
    cfg = SHEET_IDS["parametros"][lang]
    df = _ler(cfg, worksheet_name="Saida_parametros" if lang == "pt" else "dados")
    if lang == "en":
        df.rename(columns=_EN_COLS_FICHAS_PARAMS, inplace=True)
        if "Eixo" in df.columns:
            df["Eixo"] = df["Eixo"].replace(_EN_EIXO)
    if "Eixo" in df.columns:
        df["Eixo"] = df["Eixo"].astype(str).apply(_normalizar)
    if "Nível" in df.columns:
        df["Nível"] = (
            df["Nível"].astype(str).str.replace(r"^Level\s+(\d+)$", r"Nível \1", regex=True)
        )
    return df


def ler_financiamento(lang: str) -> pd.DataFrame:
    """Lê a sheet Financiamento e normaliza colunas EN → PT."""
    cfg = SHEET_IDS["financiamento"][lang]
    df = _ler(cfg, worksheet_name="Financiamento_climatico" if lang == "pt" else "dados")
    if lang == "en":
        df.rename(columns=_EN_COLS_FINANCIAMENTO, inplace=True)
    return df


def ler_mapa(lang: str) -> pd.DataFrame:
    """Lê a sheet Mapa e normaliza colunas EN → PT."""
    cfg = SHEET_IDS["mapa"][lang]
    client = _get_client()
    sh = client.open_by_key(cfg["id"])
    ws = sh.get_worksheet_by_id(cfg["gid"]) if cfg["gid"] else sh.get_worksheet(0)
    dados = ws.get_all_records()
    df = pd.DataFrame(dados)
    df.columns = [str(col).strip() for col in df.columns]
    df = _corrigir_mojibake_df(df)
    if lang == "en":
        df.rename(columns=_EN_COLS_MAPA, inplace=True)
    return df
