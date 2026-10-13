import hashlib
import json
import logging
import os
import time
from datetime import timedelta

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.assistente.models import InteracaoAssistente
from apps.assistente.servico import AssistenteIndisponivel, responder
from apps.indicadores.views import _lang

logger = logging.getLogger(__name__)

MAX_PERGUNTA = 500
LIMITE_IP_DIA = int(os.environ.get("ASSISTENTE_LIMITE_IP_DIA", "20"))
LIMITE_TOTAL_DIA = int(os.environ.get("ASSISTENTE_LIMITE_TOTAL_DIA", "500"))

_MSG = {
    "pt": {
        "invalida": "Escreva uma pergunta de até 500 caracteres.",
        "limite_ip": "Você atingiu o limite de perguntas por hoje. Volte amanhã.",
        "limite_total": "O assistente atingiu o limite de uso de hoje. Tente novamente amanhã.",
        "indisponivel": "O assistente está indisponível no momento. Tente novamente mais tarde.",
    },
    "en": {
        "invalida": "Please write a question of up to 500 characters.",
        "limite_ip": "You have reached today's question limit. Please come back tomorrow.",
        "limite_total": "The assistant has reached today's usage limit. Please try tomorrow.",
        "indisponivel": "The assistant is unavailable right now. Please try again later.",
    },
}


def _ip_hash(request) -> str:
    # X-Real-IP vem do Nginx (o container so escuta em 127.0.0.1, entao e confiavel)
    ip = request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR", "")
    return hashlib.sha256(f"{settings.SECRET_KEY}:{ip}".encode()).hexdigest()


@require_POST
def perguntar(request):
    lang = _lang(request)
    msg = _MSG[lang]
    try:
        dados = json.loads(request.body or b"{}")
        pergunta = str(dados.get("pergunta", "")).strip()
        historico = dados.get("historico") or []
        if not isinstance(historico, list):
            raise ValueError
    except (ValueError, AttributeError):
        return JsonResponse({"erro": msg["invalida"]}, status=400)
    if not pergunta or len(pergunta) > MAX_PERGUNTA:
        return JsonResponse({"erro": msg["invalida"]}, status=400)

    # Limites em janela de 24h, contados no banco (vale para todos os workers do Gunicorn)
    ip_hash = _ip_hash(request)
    hoje = InteracaoAssistente.objects.filter(
        criado_em__gte=timezone.now() - timedelta(days=1), erro=""
    )
    if hoje.filter(ip_hash=ip_hash).count() >= LIMITE_IP_DIA:
        return JsonResponse({"erro": msg["limite_ip"]}, status=429)
    if hoje.count() >= LIMITE_TOTAL_DIA:
        return JsonResponse({"erro": msg["limite_total"]}, status=429)

    registro = InteracaoAssistente(lang=lang, ip_hash=ip_hash, pergunta=pergunta)
    inicio = time.monotonic()
    try:
        r = responder(pergunta, historico, lang)
    except AssistenteIndisponivel as e:
        registro.erro = str(e)[:200]
        registro.latencia_ms = int((time.monotonic() - inicio) * 1000)
        registro.save()
        logger.warning("Assistente indisponivel: %s", e)
        return JsonResponse({"erro": msg["indisponivel"]}, status=503)

    registro.resposta = r["resposta"]
    registro.fontes = r["fontes"]
    registro.modelo = r["modelo"]
    registro.tokens_entrada = r["tokens_entrada"]
    registro.tokens_saida = r["tokens_saida"]
    registro.latencia_ms = int((time.monotonic() - inicio) * 1000)
    registro.save()
    return JsonResponse({"resposta": r["resposta"], "fontes": r["fontes"]})
