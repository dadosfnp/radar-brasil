from django.shortcuts import render
from django.http import JsonResponse
from apps.indicadores.services.painel_multinivel import dados_para_grafico


def painel_multinivel_view(request):
    return render(request, "municipios/painel-multinivel.html")


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