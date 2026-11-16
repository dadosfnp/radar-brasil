from django.shortcuts import render

from apps.indicadores.services.painel_multinivel import (
    EIXO_MAP,
    NOME_EIXO_EN,
    NOME_EIXO_PT,
    dados_para_grafico,
)

# Imagem de fundo do card de cada eixo na Landing (mesma usada no Painel ▸ Visão Geral)
_EIXO_IMAGEM = {
    "Governanca": "shutterstock_2551759713.jpg.jpeg",
    "Politicas e Planos": "shutterstock_2077744378.jpg.jpeg",
    "Programas": "shutterstock_2495902353.jpg.jpeg",
    "Linhas de Financiamento": "shutterstock_614431316.jpg.jpeg",
}


def inicio(request):
    return render(request, "municipios/inicio.html")


def sobre(request):
    return render(request, "municipios/sobre.html")


def metodologia(request):
    return render(request, "municipios/metodologia.html")


def landing(request):
    lang = "en" if str(getattr(request, "LANGUAGE_CODE", "pt-br")).startswith("en") else "pt"
    nomes = NOME_EIXO_EN if lang == "en" else NOME_EIXO_PT

    eixos_resumo = []
    for eixo_front in EIXO_MAP:
        try:
            dados = dados_para_grafico(eixo_front, lang=lang)
        except Exception:
            dados = {}
        eixos_resumo.append(
            {
                "nome": nomes.get(eixo_front, eixo_front),
                "descricao": dados.get("descricao_eixo", ""),
                "nivel": dados.get("nivel_eixo"),
                "imagem": _EIXO_IMAGEM.get(eixo_front),
            }
        )

    return render(request, "municipios/landing.html", {"eixos_resumo": eixos_resumo})
