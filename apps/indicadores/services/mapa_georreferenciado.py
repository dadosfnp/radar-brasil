import json
import os

from apps.indicadores.models import RegistroMapa

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

_coords_cache = None
_nome_idx = None


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
    if code_muni:
        c = coords.get(code_muni)
        if c:
            return c
    if municipio and _nome_idx is not None:
        key = f"{municipio.lower().strip()}|{uf}"
        c = _nome_idx.get(key)
        if c:
            return c
    return None


# ── API pública ───────────────────────────────────────────────────


def get_dados_mapa(lang: str = "pt") -> dict:
    coords = _load_coords()
    registros = list(RegistroMapa.objects.filter(lang=lang))

    # Agrega por município
    muni: dict = {}
    for reg in registros:
        c = _lookup_coords(reg.code_muni, reg.municipio, reg.uf)
        if c is None:
            continue

        key = reg.code_muni if reg.code_muni else f"\x00{reg.municipio.lower().strip()}|{reg.uf}"

        if key not in muni:
            muni[key] = {
                "c": c,
                "code_muni": reg.code_muni,
                "municipio": reg.municipio,
                "uf": reg.uf,
                "populacao": reg.populacao,
                "unico_ests": [],
                "agrupado_emps": {},
                "agrupado_prog_keys": set(),
                "programas": [],
                "eixos": set(),
                "modalidades": set(),
                "estagios": set(),
                "executores": set(),
                "first": None,
            }

        d = muni[key]
        est = reg.estimativa_2023_2030
        pct = reg.percentual_executado

        programa_entry = {
            "empreendimento": reg.empreendimento,
            "perfil": reg.perfil,
            "estagio": reg.estagio,
            "estimativa": est,
            "percentual": pct,
            "executor": reg.tipo_executor,
            "modalidade": reg.modalidade,
            "eixo": reg.eixo,
        }

        if reg.perfil == "Investimento Único":
            d["unico_ests"].append(est)
            d["programas"].append(programa_entry)
        else:
            if reg.empreendimento not in d["agrupado_emps"]:
                d["agrupado_emps"][reg.empreendimento] = est
            prog_key = (reg.empreendimento, reg.estagio)
            if prog_key not in d["agrupado_prog_keys"]:
                d["agrupado_prog_keys"].add(prog_key)
                d["programas"].append(programa_entry)

        for val, s in [
            (reg.eixo, d["eixos"]),
            (reg.modalidade, d["modalidades"]),
            (reg.estagio, d["estagios"]),
            (reg.tipo_executor, d["executores"]),
        ]:
            if val and val != "nan":
                s.add(val)

        if d["first"] is None:
            d["first"] = programa_entry

    by_code = {d["code_muni"]: k for k, d in muni.items() if d["code_muni"]}
    by_name = {f"{d['municipio'].lower().strip()}|{d['uf']}": k for k, d in muni.items()}

    features = []
    for code_muni, c in coords.items():
        uf = c.get("uf", "")
        nom = c.get("nome", "")
        porte = c.get("porte", "")

        lookup_key = by_code.get(code_muni) or by_name.get(f"{nom.lower().strip()}|{uf}")
        d = muni.get(lookup_key) if lookup_key else None

        if d:
            unico_min = min(d["unico_ests"]) if d["unico_ests"] else 0
            n_prog = len(d["programas"])
            first = d["first"] or {}
            estimativa_total = sum(p.get("estimativa", 0) for p in d["programas"])

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
                        "populacao": d.get("populacao", ""),
                        "tem_financiamento": True,
                        "n_programas": n_prog,
                        "unico_min_est": unico_min,
                        "agrupado_empreendimentos": [
                            {"nome": k, "estimativa": v} for k, v in d["agrupado_emps"].items()
                        ],
                        "eixo": first.get("eixo", ""),
                        "eixos": list(d["eixos"]),
                        "modalidade": first.get("modalidade", ""),
                        "modalidades": list(d["modalidades"]),
                        "estagio": first.get("estagio", ""),
                        "estagios": list(d["estagios"]),
                        "executor": first.get("executor", ""),
                        "executores": list(d["executores"]),
                        "programas": d["programas"],
                        "perfil": first.get("perfil", ""),
                        "empreendimento": first.get("empreendimento", ""),
                        "estimativa": first.get("estimativa", 0),
                        "estimativa_total": estimativa_total,
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


def get_filtros_mapa(lang: str = "pt") -> dict:
    qs = RegistroMapa.objects.filter(lang=lang)

    def uniq(field):
        return sorted({v for v in qs.values_list(field, flat=True).distinct() if v and v != "nan"})

    ufs = uniq("uf")
    regioes = sorted({REGIAO_POR_UF.get(uf, "") for uf in ufs if uf})

    return {
        "eixos": uniq("eixo"),
        "modalidades": uniq("modalidade"),
        "estagios": uniq("estagio"),
        "executores": uniq("tipo_executor"),
        "perfis": uniq("perfil"),
        "ufs": ufs,
        "regioes": [r for r in regioes if r],
    }
