import os
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ── Configuração ──────────────────────────────────────────────
CREDS_PATH = ".secrets/fnp-radar-sheets.json"
SHEET_ID   = "1L5uuiTqoz9aDUAVflGww1UnZfp7xFntcmvoB_jeS3Og"

CORES_NIVEL = {
    0: "#d73027",
    1: "#f46d43",
    2: "#fdae61",
    3: "#fee08b",
    4: "#a6d96a",
    5: "#1a9850",
}

EIXOS = {
    "Governanca":             "Governança",
    "Politicas e Planos":     "Políticas e Planos",
    "Programas":              "Programas",
    "Linhas de Financiamento":"Linhas de Financiamento",
}

# Mapeamento: nome do eixo → nome da aba na planilha
ABA_MAP = {
    "Governanca":             "Governança",
    "Politicas e Planos":     "Políticas e Planos",
    "Programas":              "Programas",
    "Linhas de Financiamento":"Linhas de Financiamento",
}

# Tipos de parâmetro (ordem fixa igual ao R)
TIPOS = [
    "Operacionalidade",
    "Espaço de diálogo federativo",
    "Financiamento",
    "Representação de Gênero, Raça e Etnia",
    "Comunicação e Transparência",
]


def _get_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds  = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, scope)
    return gspread.authorize(creds)


def _ler_aba(client, aba_nome: str) -> pd.DataFrame:
    """Lê a aba e devolve um DataFrame bruto (sem tratamento)."""
    sheet = client.open_by_key(SHEET_ID)
    ws    = sheet.worksheet(aba_nome)
    dados = ws.get_all_values()
    return pd.DataFrame(dados)


def _processar_governanca(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Replica o bloco R:
      governanca_limp → Governanca_parametro → pivot_longer
    Devolve colunas: Estrutura, Setor, Tipo, Nivel, Avaliacao, Descritivo
    """
    # Linha 0 = cabeçalho geral (ignorar)
    # Linha 1 = sub-cabeçalho com nomes dos parâmetros
    # Linha 2 = nomes das colunas finais
    # Dados a partir da linha 3

    # Índices das colunas de parâmetros (igual ao select do R: cols 10-24)
    # Col 0  = Estrutura
    # Col 1  = Setor
    # Col 10 = Nível Operacionalidade
    # Col 11 = Avaliação Operacionalidade
    # Col 12 = Descritivo Operacionalidade
    # Col 13 = Nível Diálogo
    # ... e assim por diante (3 colunas por tipo)

    dados = df_raw.iloc[3:].reset_index(drop=True)  # remove as 3 linhas de cabeçalho
    dados.columns = range(len(dados.columns))

    registros = []
    for _, row in dados.iterrows():
        estrutura = str(row[0]).strip()
        setor     = str(row[1]).strip()

        if not estrutura or estrutura.lower() in ("", "nan"):
            continue

        # Cada tipo ocupa 3 colunas: Nível, Avaliação, Descritivo
        inicio_col = 10  # mesma lógica do R: select(1:2, 10:24)
        for i, tipo in enumerate(TIPOS):
            col_nivel     = inicio_col + (i * 3)
            col_avaliacao = col_nivel + 1
            col_descritivo= col_nivel + 2

            try:
                nivel_raw = str(row[col_nivel]).strip()
                nivel     = int(float(nivel_raw)) if nivel_raw not in ("", "nan") else None
            except (ValueError, IndexError):
                nivel = None

            try:
                avaliacao  = str(row[col_avaliacao]).strip()
            except IndexError:
                avaliacao = ""

            try:
                descritivo = str(row[col_descritivo]).strip()
            except IndexError:
                descritivo = ""

            registros.append({
                "Estrutura":  estrutura,
                "Setor":      setor,
                "Tipo":       tipo,
                "Nivel":      nivel,
                "Avaliacao":  avaliacao,
                "Descritivo": descritivo,
                "Eixo":       "Governanca",
            })

    return pd.DataFrame(registros)


def _processar_generica(df_raw: pd.DataFrame, eixo: str) -> pd.DataFrame:
    """
    Processamento genérico para Políticas e Planos, Programas e
    Linhas de Financiamento — mesma lógica de colunas.
    """
    dados = df_raw.iloc[3:].reset_index(drop=True)
    dados.columns = range(len(dados.columns))

    registros = []
    for _, row in dados.iterrows():
        estrutura = str(row[0]).strip()
        setor     = str(row[1]).strip()

        if not estrutura or estrutura.lower() in ("", "nan"):
            continue

        inicio_col = 10
        for i, tipo in enumerate(TIPOS):
            col_nivel     = inicio_col + (i * 3)
            col_avaliacao = col_nivel + 1
            col_descritivo= col_nivel + 2

            try:
                nivel_raw = str(row[col_nivel]).strip()
                nivel     = int(float(nivel_raw)) if nivel_raw not in ("", "nan") else None
            except (ValueError, IndexError):
                nivel = None

            try:
                avaliacao  = str(row[col_avaliacao]).strip()
            except IndexError:
                avaliacao = ""

            try:
                descritivo = str(row[col_descritivo]).strip()
            except IndexError:
                descritivo = ""

            registros.append({
                "Estrutura":  estrutura,
                "Setor":      setor,
                "Tipo":       tipo,
                "Nivel":      nivel,
                "Avaliacao":  avaliacao,
                "Descritivo": descritivo,
                "Eixo":       eixo,
            })

    return pd.DataFrame(registros)


def dados_para_grafico(eixo: str) -> dict:
    """
    Função principal chamada pela view Django.
    Retorna o JSON pronto para o Chart.js:
    {
        "labels": ["Operacionalidade", ...],
        "datasets": [
            {"label": "Nível 0", "data": [3, 1, 2, 0, 1], "backgroundColor": "#d73027"},
            ...
        ]
    }
    """
    client   = _get_client()
    aba_nome = ABA_MAP.get(eixo, "Governança")
    df_raw   = _ler_aba(client, aba_nome)

    if eixo == "Governanca":
        df = _processar_governanca(df_raw)
    else:
        df = _processar_generica(df_raw, eixo)

    # Remove linhas sem nível
    df = df.dropna(subset=["Nivel"])
    df["Nivel"] = df["Nivel"].astype(int)

    # Agrupa: conta quantas estruturas estão em cada Nível, por Tipo
    agrupado = (
        df.groupby(["Tipo", "Nivel"])
        .size()
        .reset_index(name="Contagem")
    )

    # Garante ordem fixa dos tipos (igual ao R)
    labels   = TIPOS
    datasets = []

    for nivel in range(6):  # 0 a 5
        contagens = []
        for tipo in labels:
            filtro = agrupado[
                (agrupado["Tipo"] == tipo) & (agrupado["Nivel"] == nivel)
            ]
            contagens.append(int(filtro["Contagem"].sum()))

        datasets.append({
            "label":           f"Nível {nivel}",
            "data":            contagens,
            "backgroundColor": CORES_NIVEL[nivel],
            "borderWidth":     0,
        })

    return {
        "labels":   labels,
        "datasets": datasets,
    }