import logging

from django.shortcuts import render
from django.http import JsonResponse
from apps.indicadores.services.painel_multinivel import dados_para_grafico, get_total_municipios

logger = logging.getLogger(__name__)

_EIXOS_VALIDOS = {"Governanca", "Politicas e Planos", "Programas", "Linhas de Financiamento"}
_ERRO_GENERICO = "Erro ao processar a requisição."


def _lang(request) -> str:
    code = getattr(request, "LANGUAGE_CODE", "pt-br")
    return "en" if str(code).startswith("en") else "pt"


def _eixo_valido(request):
    eixo = request.GET.get("eixo", "Governanca")
    if eixo not in _EIXOS_VALIDOS:
        return None, JsonResponse({"erro": "Parâmetro inválido."}, status=400)
    return eixo, None


def painel_multinivel_view(request):
    try:
        total_municipios = get_total_municipios(lang=_lang(request))
    except Exception:
        total_municipios = "—"
    return render(
        request, "municipios/painel-multinivel.html", {"total_municipios": total_municipios}
    )


def api_painel_multinivel(request):
    eixo, err = _eixo_valido(request)
    if err:
        return err
    try:
        dados = dados_para_grafico(eixo, lang=_lang(request))
        return JsonResponse(dados)
    except Exception:
        logger.exception("Erro em api_painel_multinivel")
        return JsonResponse({"erro": _ERRO_GENERICO}, status=500)


def avaliacao_painel_view(request):
    return render(request, "municipios/avaliacao-painel.html")


def api_avaliacao_filtros(request):
    eixo, err = _eixo_valido(request)
    if err:
        return err
    try:
        from apps.indicadores.services.avaliacao_painel import get_filtros

        return JsonResponse(get_filtros(eixo, lang=_lang(request)))
    except Exception:
        logger.exception("Erro em api_avaliacao_filtros")
        return JsonResponse({"erro": _ERRO_GENERICO}, status=500)


def api_avaliacao_tabela(request):
    estrutura = request.GET.get("estrutura", "").strip()
    if not estrutura:
        return JsonResponse({"rows": []})
    try:
        from apps.indicadores.services.avaliacao_painel import get_tabela

        return JsonResponse({"rows": get_tabela(estrutura, lang=_lang(request))})
    except Exception:
        logger.exception("Erro em api_avaliacao_tabela")
        return JsonResponse({"erro": _ERRO_GENERICO}, status=500)


def api_avaliacao_ficha(request):
    estrutura = request.GET.get("estrutura", "").strip()
    if not estrutura:
        return JsonResponse({"campos": []})
    try:
        from apps.indicadores.services.avaliacao_painel import get_ficha

        return JsonResponse(get_ficha(estrutura, lang=_lang(request)))
    except Exception:
        logger.exception("Erro em api_avaliacao_ficha")
        return JsonResponse({"erro": _ERRO_GENERICO}, status=500)


def linha_do_tempo_view(request):
    estrutura = request.GET.get("estrutura", "").strip()
    return render(request, "municipios/linha-do-tempo.html", {"estrutura": estrutura})


def mapa_georreferenciado_view(request):
    return render(request, "municipios/mapa-georreferenciado.html")


def api_mapa_dados(request):
    try:
        from apps.indicadores.services.mapa_georreferenciado import get_dados_mapa

        return JsonResponse(get_dados_mapa(lang=_lang(request)))
    except Exception:
        logger.exception("Erro em api_mapa_dados")
        return JsonResponse({"erro": _ERRO_GENERICO}, status=500)


def api_mapa_filtros(request):
    try:
        from apps.indicadores.services.mapa_georreferenciado import get_filtros_mapa

        return JsonResponse(get_filtros_mapa(lang=_lang(request)))
    except Exception:
        logger.exception("Erro em api_mapa_filtros")
        return JsonResponse({"erro": _ERRO_GENERICO}, status=500)


def nota_pais_view(request):
    return render(request, "municipios/nota-pais.html")


def financiamento_climatico_view(request):
    return render(request, "municipios/financiamento-climatico.html")


def api_fin_cli_filtros(request):
    try:
        from apps.indicadores.services.financiamento_climatico import get_filtros

        return JsonResponse(get_filtros(lang=_lang(request)))
    except Exception:
        logger.exception("Erro em api_fin_cli_filtros")
        return JsonResponse({"erro": _ERRO_GENERICO}, status=500)


def api_fin_cli_tabela(request):
    filtros = {
        "programa": request.GET.get("programa", "").strip(),
        "setor": request.GET.get("setor", "").strip(),
        "modalidade": request.GET.get("modalidade", "").strip(),
        "origem": request.GET.get("origem", "").strip(),
        "ente": request.GET.get("ente", "").strip(),
    }
    try:
        from apps.indicadores.services.financiamento_climatico import get_tabela

        return JsonResponse({"rows": get_tabela(filtros, lang=_lang(request))})
    except Exception:
        logger.exception("Erro em api_fin_cli_tabela")
        return JsonResponse({"erro": _ERRO_GENERICO}, status=500)


def api_fin_cli_graficos(request):
    filtros = {
        "programa": request.GET.get("programa", "").strip(),
        "setor": request.GET.get("setor", "").strip(),
        "modalidade": request.GET.get("modalidade", "").strip(),
        "origem": request.GET.get("origem", "").strip(),
        "ente": request.GET.get("ente", "").strip(),
    }
    try:
        from apps.indicadores.services.financiamento_climatico import get_graficos

        return JsonResponse(get_graficos(filtros, lang=_lang(request)))
    except Exception:
        logger.exception("Erro em api_fin_cli_graficos")
        return JsonResponse({"erro": _ERRO_GENERICO}, status=500)
