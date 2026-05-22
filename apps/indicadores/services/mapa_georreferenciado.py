import os
import json
import time
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

CREDS_PATH = ".secrets/fnp-radar-sheets.json"
SHEET_ID = "1un9DCK_ZGdqe54xapZbQAl4hscyBX5O0E93orhiDiyA"
SHEET_GID = 1543493122
CACHE_TTL = 1800

COORDS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "municipios_coords.json")

REGIAO_POR_UF = {
    "AC": "Norte",
    "AM": "Norte",
    "AP": "Norte",
    "PA": "Norte",
    "RO": "Norte",
    "RR": "Norte",
    "TO": "Norte",
    "AL": "Nordeste",
    "BA": "Nordeste",
    "CE": "Nordeste",
    "MA": "Nordeste",
    "PB": "Nordeste",
    "PE": "Nordeste",
    "PI": "Nordeste",
    "RN": "Nordeste",
    "SE": "Nordeste",
    "DF": "Centro-Oeste",
    "GO": "Centro-Oeste",
    "MS": "Centro-Oeste",
    "MT": "Centro-Oeste",
    "ES": "Sudeste",
    "MG": "Sudeste",
    "RJ": "Sudeste",
    "SP": "Sudeste",
    "PR": "Sul",
    "RS": "Sul",
    "SC": "Sul",
}

_cache_sheet = {"df": None, "ts": 0}
_coords_cache = None
_nome_idx = None  # "nome_lower|UF" → entry


def _parse_pct(v) -> float:
    """Retorna percentual em escala 0-100.
    Aceita: float decimal (0.75→75), inteiro (75), string '75%', formato BR '75,5'.
    gspread devolve colunas formatadas como % no Sheets como decimais (0.45 = 45%).
    """
    try:
        if v in (None, "", "nan"):
            return 0.0
        s = str(v).strip()
        if s.endswith("%"):
            s = s[:-1].strip()
        if "," in s and "." not in s:
            s = s.replace(",", ".")
        f = float(s)
    except (TypeError, ValueError):
        return 0.0
    if 0 < f <= 1:
        return round(f * 100, 1)
    return round(f, 1)


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
    if _cache_sheet["df"] is not None and (agora - _cache_sheet["ts"]) < CACHE_TTL:
        return _cache_sheet["df"]
    client = _get_client()
    ws = client.open_by_key(SHEET_ID).get_worksheet_by_id(SHEET_GID)
    dados = ws.get_all_records()
    df = pd.DataFrame(dados)
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
            uf = c.get("uf", "")
            if nome:
                _nome_idx[f"{nome}|{uf}"] = c
    except Exception:
        _coords_cache = {}
        _nome_idx = {}
    return _coords_cache


def _lookup_coords(code_muni: str, municipio: str, uf: str):
    coords = _load_coords()
    if code_muni and code_muni != "0":
        c = coords.get(code_muni)
        if c:
            return c
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
    """
    Retorna um GeoJSON com UM feature por município (todos os 5.571 do Brasil).
    Municípios com financiamento: tem_financiamento=True + dados agregados.
    Municípios sem financiamento: tem_financiamento=False + dados geográficos apenas.
    Replica a lógica do app R: distinct(code_muni) + radius por porte populacional.
    """
    df = _ler_sheet()
    coords = _load_coords()

    municipio_col = _col(df, "Municípios", "Municipios", "Município", "Municipio")
    estagio_col = _col(df, "Estágio", "Estagio")

    # ── Agrega dados de financiamento por município ────────────────
    muni = {}  # key → dict com dados agregados

    for _, row in df.iterrows():
        raw_code = str(row.get("code_muni", "")).strip()
        code_muni = str(int(float(raw_code))) if raw_code not in ("", "nan", "0") else "0"
        uf = str(row.get("UF", "")).strip()
        mun = str(row.get(municipio_col, "")).strip() if municipio_col else ""

        c = _lookup_coords(code_muni, mun, uf)
        if c is None:
            continue

        # Chave estável: código IBGE ou fallback por nome+UF
        key = code_muni if code_muni != "0" else f"\x00{mun.lower().strip()}|{uf}"

        perfil = str(row.get("Perfil", "")).strip()
        est = float(row.get("Estimativa_2023_2030", 0) or 0)
        emp = str(row.get("Empreendimento", "")).strip()
        eixo = str(row.get("Eixo", "")).strip()
        mod = str(row.get("Modalidade", "")).strip()
        etap = str(row.get(estagio_col, "")).strip() if estagio_col else ""
        exec_ = str(row.get("Tipo de Executor", "")).strip()
        pct = _parse_pct(row.get("Percentual_executado", 0))
        if pct == 0 and etap.lower() in ("concluído", "concluido"):
            pct = 100.0

        if key not in muni:
            muni[key] = {
                "c": c,
                "code_muni": code_muni,
                "municipio": mun,
                "uf": uf,
                "unico_ests": [],  # estimativas de Investimento Único
                "agrupado_emps": {},  # empreendimento → estimativa (Agrupado)
                "agrupado_prog_keys": set(),  # (emp, estagio) já adicionados
                "programas": [],  # lista completa para exibição no popup
                "eixos": set(),
                "modalidades": set(),
                "estagios": set(),
                "executores": set(),
                "first": None,
            }

        d = muni[key]

        if perfil == "Investimento Único":
            d["unico_ests"].append(est)
            d["programas"].append(
                {
                    "empreendimento": emp,
                    "perfil": perfil,
                    "estagio": etap,
                    "estimativa": est,
                    "percentual": pct,
                    "executor": exec_,
                    "modalidade": mod,
                    "eixo": eixo,
                }
            )
        else:
            if emp not in d["agrupado_emps"]:
                d["agrupado_emps"][emp] = est  # dedup financeiro por empreendimento
            prog_key = (emp, etap)
            if prog_key not in d["agrupado_prog_keys"]:
                d["agrupado_prog_keys"].add(prog_key)
                d["programas"].append(
                    {
                        "empreendimento": emp,
                        "perfil": perfil,
                        "estagio": etap,
                        "estimativa": est,
                        "percentual": pct,
                        "executor": exec_,
                        "modalidade": mod,
                        "eixo": eixo,
                    }
                )

        for val, s in [
            (eixo, d["eixos"]),
            (mod, d["modalidades"]),
            (etap, d["estagios"]),
            (exec_, d["executores"]),
        ]:
            if val and val != "nan":
                s.add(val)

        if d["first"] is None:
            d["first"] = {
                "empreendimento": emp,
                "modalidade": mod,
                "estagio": etap,
                "estimativa": est,
                "percentual": pct,
                "executor": exec_,
                "perfil": perfil,
                "eixo": eixo,
            }

    # Índices de lookup para cruzar com coords
    by_code = {d["code_muni"]: k for k, d in muni.items() if d["code_muni"] != "0"}
    by_name = {f"{d['municipio'].lower().strip()}|{d['uf']}": k for k, d in muni.items()}

    # ── Gera um feature para cada município do Brasil ──────────────
    features = []

    for code_muni, c in coords.items():
        uf = c.get("uf", "")
        nom = c.get("nome", "")
        porte = c.get("porte", "")

        # Tenta localizar dados de financiamento
        lookup_key = by_code.get(code_muni) or by_name.get(f"{nom.lower().strip()}|{uf}")
        d = muni.get(lookup_key) if lookup_key else None

        if d:
            unico_min = min(d["unico_ests"]) if d["unico_ests"] else 0
            n_prog = len(d["programas"])
            first = d["first"] or {}

            features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [c["lng"], c["lat"]]},
                    "properties": {
                        "code_muni": code_muni,
                        "municipio": nom,
                        "uf": uf,
                        "regiao": REGIAO_POR_UF.get(uf, ""),
                        "porte": porte,
                        # flags para visualização (replica R: tem_financiamento)
                        "tem_financiamento": True,
                        "n_programas": n_prog,
                        # campos para cálculo do painel de totais
                        "unico_min_est": unico_min,
                        "agrupado_empreendimentos": [
                            {"nome": k, "estimativa": v} for k, v in d["agrupado_emps"].items()
                        ],
                        # campos para filtros (múltiplos valores por município)
                        "eixo": first.get("eixo", ""),
                        "eixos": list(d["eixos"]),
                        "modalidade": first.get("modalidade", ""),
                        "modalidades": list(d["modalidades"]),
                        "estagio": first.get("estagio", ""),
                        "estagios": list(d["estagios"]),
                        "executor": first.get("executor", ""),
                        "executores": list(d["executores"]),
                        # campos para popup
                        "programas": d["programas"],
                        "perfil": first.get("perfil", ""),
                        "empreendimento": first.get("empreendimento", ""),
                        "estimativa": first.get("estimativa", 0),
                        "percentual": first.get("percentual", 0),
                    },
                }
            )
        else:
            features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [c["lng"], c["lat"]]},
                    "properties": {
                        "code_muni": code_muni,
                        "municipio": nom,
                        "uf": uf,
                        "regiao": REGIAO_POR_UF.get(uf, ""),
                        "porte": porte,
                        "tem_financiamento": False,
                        "n_programas": 0,
                        "unico_min_est": 0,
                        "agrupado_empreendimentos": [],
                        "eixo": "",
                        "eixos": [],
                        "modalidade": "",
                        "modalidades": [],
                        "estagio": "",
                        "estagios": [],
                        "executor": "",
                        "executores": [],
                        "perfil": "",
                        "empreendimento": "",
                        "estimativa": 0,
                        "percentual": 0,
                    },
                }
            )

    return {"type": "FeatureCollection", "features": features}


def get_filtros_mapa() -> dict:
    df = _ler_sheet()

    def uniq(col, *alts):
        name = _col(df, col, *alts)
        if not name:
            return []
        return sorted({v for v in df[name].astype(str).str.strip() if v not in ("", "nan")})

    ufs = uniq("UF")
    regioes = sorted({REGIAO_POR_UF.get(uf, "") for uf in ufs if uf})

    return {
        "eixos": uniq("Eixo"),
        "modalidades": uniq("Modalidade"),
        "estagios": uniq("Estágio", "Estagio"),
        "executores": uniq("Tipo de Executor"),
        "perfis": uniq("Perfil"),
        "ufs": ufs,
        "regioes": [r for r in regioes if r],
    }
