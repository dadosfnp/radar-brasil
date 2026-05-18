from django.shortcuts import render
from django.http import JsonResponse
from apps.indicadores.services.painel_multinivel import dados_para_grafico, get_total_municipios


def painel_multinivel_view(request):
    try:
        total_municipios = get_total_municipios()
    except Exception:
        total_municipios = "—"
    return render(request, "municipios/painel-multinivel.html", {"total_municipios": total_municipios})


def api_painel_multinivel(request):
    eixo = request.GET.get("eixo", "Governanca")
    try:
        dados = dados_para_grafico(eixo)
        return JsonResponse(dados)
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


def avaliacao_painel_view(request):
    return render(request, "municipios/avaliacao-painel.html")


def api_avaliacao_filtros(request):
    eixo = request.GET.get("eixo", "Governanca")
    try:
        from apps.indicadores.services.avaliacao_painel import get_filtros
        return JsonResponse(get_filtros(eixo))
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


def api_avaliacao_tabela(request):
    estrutura = request.GET.get("estrutura", "")
    if not estrutura:
        return JsonResponse({"rows": []})
    try:
        from apps.indicadores.services.avaliacao_painel import get_tabela
        return JsonResponse({"rows": get_tabela(estrutura)})
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


def api_avaliacao_ficha(request):
    estrutura = request.GET.get("estrutura", "")
    if not estrutura:
        return JsonResponse({"campos": []})
    try:
        from apps.indicadores.services.avaliacao_painel import get_ficha
        return JsonResponse(get_ficha(estrutura))
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


def linha_do_tempo_view(request):
    estrutura = request.GET.get("estrutura", "")
    return render(request, "municipios/linha-do-tempo.html", {"estrutura": estrutura})


def mapa_georreferenciado_view(request):
    return render(request, "municipios/mapa-georreferenciado.html")


def api_mapa_dados(request):
    try:
        from apps.indicadores.services.mapa_georreferenciado import get_dados_mapa
        return JsonResponse(get_dados_mapa())
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


def api_mapa_filtros(request):
    try:
        from apps.indicadores.services.mapa_georreferenciado import get_filtros_mapa
        return JsonResponse(get_filtros_mapa())
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


def nota_pais_view(request):
    return render(request, "municipios/nota-pais.html")


def financiamento_climatico_view(request):
    return render(request, "municipios/financiamento-climatico.html")


def api_fin_cli_filtros(request):
    try:
        from apps.indicadores.services.financiamento_climatico import get_filtros
        return JsonResponse(get_filtros())
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


def api_fin_cli_tabela(request):
    filtros = {
        "programa":   request.GET.get("programa", ""),
        "setor":      request.GET.get("setor", ""),
        "modalidade": request.GET.get("modalidade", ""),
        "origem":     request.GET.get("origem", ""),
        "ente":       request.GET.get("ente", ""),
    }
    try:
        from apps.indicadores.services.financiamento_climatico import get_tabela
        return JsonResponse({"rows": get_tabela(filtros)})
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


def api_fin_cli_graficos(request):
    filtros = {
        "programa":   request.GET.get("programa", ""),
        "setor":      request.GET.get("setor", ""),
        "modalidade": request.GET.get("modalidade", ""),
        "origem":     request.GET.get("origem", ""),
        "ente":       request.GET.get("ente", ""),
    }
    try:
        from apps.indicadores.services.financiamento_climatico import get_graficos
        return JsonResponse(get_graficos(filtros))
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)