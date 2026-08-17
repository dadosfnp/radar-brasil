"""
Leitor de Google Sheets — uso exclusivo do comando sync_sheets_db.
Centraliza o acesso via gspread para importação de dados para o PostgreSQL.
Os services de indicadores NÃO importam este módulo; eles leem direto do banco.
"""

import json
import os
import unicodedata

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

CREDS_PATH = ".secrets/fnp-radar-sheets.json"

# ── IDs das planilhas ────────────────────────────────────────────
SHEET_IDS = {
    "fichas": {
        "pt": {"id": "16s59h5uE0R6GZTkrjQZI152gUOjfjxeOeAwy7v6JYH8", "gid": None},
        "en": {"id": "1EkaWJ2n391vXukwsNTGj-RMd65S55hADtR24lxRXx9g", "gid": 1400373985},
    },
    "parametros": {
        "pt": {"id": "1jKGDhsjDYHRKEJCLdP-5zCxCSh5q5A5t8x1RhErmEoE", "gid": None},
        "en": {"id": "1t-ivtzjEbn4qneUZr9vaRwCgq7iGKTmIHUnM0aBp4f8", "gid": 1708988989},
    },
    "financiamento": {
        "pt": {"id": "1sxKa2yu8GL8U6m4zoK42hO75a-YZqVKK5PKNJ8jlJ8c", "gid": 793540087},
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
    return df


def ler_fichas(lang: str) -> pd.DataFrame:
    """Lê a sheet Fichas e normaliza colunas + eixo para forma canônica PT."""
    cfg = SHEET_IDS["fichas"][lang]
    df = _ler(cfg)
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
    df = _ler(cfg)
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
    client = _get_client()
    sh = client.open_by_key(cfg["id"])
    ws = sh.get_worksheet_by_id(cfg["gid"])
    dados = ws.get_all_records()
    df = pd.DataFrame(dados)
    df.columns = [str(col).strip() for col in df.columns]
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
    if lang == "en":
        df.rename(columns=_EN_COLS_MAPA, inplace=True)
    return df
