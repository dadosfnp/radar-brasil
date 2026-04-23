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