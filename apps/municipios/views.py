from django.shortcuts import redirect, render

from apps.indicadores.services.painel_multinivel import (
    EIXO_MAP,
    NOME_EIXO_EN,
    NOME_EIXO_ES,
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
    # Pagina antiga, substituida pela Landing (reestruturacao de 2026-11-16) — o link
    # ja saiu do menu, mas a rota continuava acessivel direto e mostrava o design antigo
    # fora de uso (achado em 2026-11-20). Redireciona pra Landing em vez de apagar a rota.
    return redirect("municipios:home", permanent=True)


def sobre(request):
    return render(request, "municipios/sobre.html")


def metodologia(request):
    return render(request, "municipios/metodologia.html")


def landing(request):
    codigo = str(getattr(request, "LANGUAGE_CODE", "pt-br"))
    if codigo.startswith("en"):
        lang = "en"
    elif codigo.startswith("es"):
        lang = "es"
    else:
        lang = "pt"
    nomes = {"en": NOME_EIXO_EN, "es": NOME_EIXO_ES}.get(lang, NOME_EIXO_PT)

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
