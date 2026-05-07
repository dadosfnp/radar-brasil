import os
import json
import time
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

CREDS_PATH = ".secrets/fnp-radar-sheets.json"
SHEET_ID   = "1un9DCK_ZGdqe54xapZbQAl4hscyBX5O0E93orhiDiyA"
SHEET_GID  = 1543493122
CACHE_TTL  = 1800

COORDS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "municipios_coords.json")

REGIAO_POR_UF = {
    "AC":"Norte","AM":"Norte","AP":"Norte","PA":"Norte","RO":"Norte","RR":"Norte","TO":"Norte",
    "AL":"Nordeste","BA":"Nordeste","CE":"Nordeste","MA":"Nordeste","PB":"Nordeste",
    "PE":"Nordeste","PI":"Nordeste","RN":"Nordeste","SE":"Nordeste",
    "DF":"Centro-Oeste","GO":"Centro-Oeste","MS":"Centro-Oeste","MT":"Centro-Oeste",
    "ES":"Sudeste","MG":"Sudeste","RJ":"Sudeste","SP":"Sudeste",
    "PR":"Sul","RS":"Sul","SC":"Sul",
}

_cache_sheet = {"df": None, "ts": 0}
_coords_cache = None
_nome_idx = None   # "nome_lower|UF" → entry


def _get_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, scope)
    return gspread.authorize(creds)


def _ler_sheet() -> pd.DataFrame:
    agora = time.time()
    if _cache_sheet["df"] is not None and (agora - _cache_sheet["ts"]) < CACHE_TTL:
        return _cache_sheet["df"]
    client = _get_client()
    ws     = client.open_by_key(SHEET_ID).get_worksheet_by_id(SHEET_GID)
    dados  = ws.get_all_records()
    df     = pd.DataFrame(dados)
    df.columns = [str(c).strip() for c in df.columns]
    _cache_sheet["df"] = df
    _cache_sheet["ts"] = agora
    return df


def _load_coords() -> dict:
    global _coords_cache, _nome_idx
    if _coords_cache is not None:
        return _coords_cache
    try:
        path = os.path.normpath(COORDS_FILE)
        with open(path, "r", encoding="utf-8") as f:
            _coords_cache = json.load(f)
        _nome_idx = {}
        for code, c in _coords_cache.items():
            nome = c.get("nome", "").lower().strip()
            uf   = c.get("uf", "")
            if nome:
                _nome_idx[f"{nome}|{uf}"] = c
    except Exception:
        _coords_cache = {}
        _nome_idx = {}
    return _coords_cache


def _lookup_coords(code_muni: str, municipio: str, uf: str):
    coords = _load_coords()
    # 1. por código IBGE (7 dígitos)
    if code_muni and code_muni != "0":
        c = coords.get(code_muni)
        if c:
            return c
    # 2. por nome + UF
    if municipio and _nome_idx is not None:
        key = f"{municipio.lower().strip()}|{uf}"
        c = _nome_idx.get(key)
        if c:
            return c
    return None


def _col(df, *names):
    for n in names:
        if n in df.columns:
            return n
    return None


def get_dados_mapa() -> dict:
    df     = _ler_sheet()
    _load_coords()

    municipio_col     = _col(df, "Municípios", "Municipios", "Município", "Municipio")
    estagio_col       = _col(df, "Estágio", "Estagio")
    classificacao_col = _col(df, "Classificação", "Classificacao")

    features = []
    for _, row in df.iterrows():
        raw_code  = str(row.get("code_muni", "")).strip()
        code_muni = str(int(float(raw_code))) if raw_code not in ("", "nan", "0") else "0"

        uf  = str(row.get("UF", "")).strip()
        mun = str(row.get(municipio_col, "")).strip() if municipio_col else ""

        c = _lookup_coords(code_muni, mun, uf)
        if c is None:
            continue

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [c["lng"], c["lat"]]},
            "properties": {
                "code_muni":      code_muni,
                "municipio":      mun,
                "uf":             uf,
                "regiao":         REGIAO_POR_UF.get(uf, ""),
                "empreendimento": str(row.get("Empreendimento", "")).strip(),
                "modalidade":     str(row.get("Modalidade", "")).strip(),
                "classificacao":  str(row.get(classificacao_col, "")).strip() if classificacao_col else "",
                "estagio":        str(row.get(estagio_col, "")).strip() if estagio_col else "",
                "estimativa":     float(row.get("Estimativa_2023_2030", 0) or 0),
                "percentual":     float(row.get("Percentual_executado", 0) or 0),
                "executor":       str(row.get("Tipo de Executor", "")).strip(),
                "perfil":         str(row.get("Perfil", "")).strip(),
                "eixo":           str(row.get("Eixo", "")).strip(),
            },
        })

    return {"type": "FeatureCollection", "features": features}


def get_filtros_mapa() -> dict:
    df = _ler_sheet()

    def uniq(col, *alts):
        name = _col(df, col, *alts)
        if not name:
            return []
        return sorted({v for v in df[name].astype(str).str.strip() if v not in ("", "nan")})

    ufs    = uniq("UF")
    regioes = sorted({REGIAO_POR_UF.get(uf, "") for uf in ufs if uf})

    return {
        "eixos":       uniq("Eixo"),
        "modalidades": uniq("Modalidade"),
        "estagios":    uniq("Estágio", "Estagio"),
        "executores":  uniq("Tipo de Executor"),
        "perfis":      uniq("Perfil"),
        "ufs":         ufs,
        "regioes":     [r for r in regioes if r],
    }
