"""
Ferramenta do Assistente para os dados do Mapa Georreferenciado (empreendimentos
do Novo PAC por municipio). Sao ~2.300 linhas tabulares por idioma: o modelo nao
recebe a tabela, chama consultar_mapa() e recebe os numeros ja agregados.
"""

import unicodedata
from collections import Counter

from apps.indicadores.models import RegistroMapa
from apps.indicadores.services.mapa_georreferenciado import REGIAO_POR_UF

MAX_EMPREENDIMENTOS = 15


def _norm(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFD", texto or "").encode("ascii", "ignore").decode()
    return sem_acento.casefold().strip()


def consultar_mapa(
    lang: str = "pt",
    municipio: str = "",
    uf: str = "",
    regiao: str = "",
    eixo: str = "",
    estagio: str = "",
) -> dict:
    """Agrega os empreendimentos que atendem a todos os filtros informados.

    Texto dos filtros: sem diferenciar acento/maiuscula; `municipio` exige nome exato,
    `eixo` e `estagio` aceitam trecho (ex.: eixo="mobilidade").
    """
    qs = RegistroMapa.objects.filter(lang="en" if lang == "en" else "pt")
    if uf:
        qs = qs.filter(uf__iexact=uf.strip())
    if regiao:
        ufs = [u for u, r in REGIAO_POR_UF.items() if _norm(r) == _norm(regiao)]
        qs = qs.filter(uf__in=ufs)

    # Filtros textuais em Python: SQLite (dev) nao tem unaccent; ~2.300 linhas no maximo.
    registros = [
        r
        for r in qs
        if (not municipio or _norm(r.municipio) == _norm(municipio))
        and (not eixo or _norm(eixo) in _norm(r.eixo))
        and (not estagio or _norm(estagio) in _norm(r.estagio))
    ]

    filtros = {
        k: v
        for k, v in {
            "municipio": municipio,
            "uf": uf,
            "regiao": regiao,
            "eixo": eixo,
            "estagio": estagio,
        }.items()
        if v
    }
    if not registros:
        return {"filtros": filtros, "total_empreendimentos": 0}

    maiores = sorted(registros, key=lambda r: r.estimativa_2023_2030, reverse=True)
    return {
        "filtros": filtros,
        "total_empreendimentos": len(registros),
        "municipios_distintos": len({(r.uf, r.municipio) for r in registros}),
        "investimento_estimado_2023_2030_reais": round(
            sum(r.estimativa_2023_2030 for r in registros), 2
        ),
        "por_estagio": dict(Counter(r.estagio for r in registros).most_common()),
        "por_eixo": dict(Counter(r.eixo for r in registros).most_common()),
        "por_tipo_executor": dict(Counter(r.tipo_executor for r in registros).most_common()),
        "maiores_empreendimentos": [
            {
                "empreendimento": r.empreendimento,
                "municipio": f"{r.municipio}/{r.uf}",
                "eixo": r.eixo,
                "estagio": r.estagio,
                "modalidade": r.modalidade,
                "percentual_executado": r.percentual_executado,
                "estimativa_2023_2030_reais": r.estimativa_2023_2030,
            }
            for r in maiores[:MAX_EMPREENDIMENTOS]
        ],
    }
