import hashlib
import json
import logging
import os
import time
import unicodedata
from datetime import timedelta

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.assistente.contexto import versao_respostas
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


def _normalizar_pergunta(texto: str) -> str:
    """ "Qual a origem do Radar Brasil?" == "qual a ORIGEM do radar brasil" (sem acento,
    caixa, espacos extras e pontuacao final)."""
    sem_acento = unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.casefold().split()).rstrip("?!. ")


def _chave_cache(pergunta: str, lang: str) -> str:
    base = f"{lang}|{versao_respostas(lang)}|{_normalizar_pergunta(pergunta)}"
    return hashlib.sha256(base.encode()).hexdigest()


def _resposta_json(registro) -> JsonResponse:
    return JsonResponse(
        {"id": registro.pk, "resposta": registro.resposta, "fontes": registro.fontes}
    )


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

    ip_hash = _ip_hash(request)
    registro = InteracaoAssistente(lang=lang, ip_hash=ip_hash, pergunta=pergunta)

    # Primeira pergunta da conversa ja respondida com os mesmos dados: reaproveita, sem
    # gastar cota (perguntas de acompanhamento dependem do historico e nao entram aqui).
    if not historico:
        registro.chave_cache = _chave_cache(pergunta, lang)
        anterior = (
            InteracaoAssistente.objects.filter(
                chave_cache=registro.chave_cache, erro="", em_cache=False
            )
            .exclude(util=False)  # resposta marcada como nao util nao e reaproveitada
            .first()
        )
        if anterior:
            registro.resposta, registro.fontes = anterior.resposta, anterior.fontes
            registro.modelo, registro.em_cache, registro.latencia_ms = anterior.modelo, True, 0
            registro.save()
            return _resposta_json(registro)

    # Limites em janela de 24h, contados no banco (vale para todos os workers do Gunicorn).
    # Respostas reaproveitadas nao contam: nao gastam cota.
    hoje = InteracaoAssistente.objects.filter(
        criado_em__gte=timezone.now() - timedelta(days=1), erro="", em_cache=False
    )
    if hoje.filter(ip_hash=ip_hash).count() >= LIMITE_IP_DIA:
        return JsonResponse({"erro": msg["limite_ip"]}, status=429)
    if hoje.count() >= LIMITE_TOTAL_DIA:
        return JsonResponse({"erro": msg["limite_total"]}, status=429)

    inicio = time.monotonic()
    try:
        r = responder(pergunta, historico, lang)
    except Exception as e:
        # Cota/sobrecarga (AssistenteIndisponivel) ou falha inesperada (rede, SDK): o
        # visitante sempre recebe a mensagem amigavel e a falha fica registrada.
        if isinstance(e, AssistenteIndisponivel):
            logger.warning("Assistente indisponivel: %s", e)
        else:
            logger.exception("Erro inesperado no assistente")
        registro.erro = f"{type(e).__name__}: {e}"[:200]
        registro.latencia_ms = int((time.monotonic() - inicio) * 1000)
        registro.save()
        return JsonResponse({"erro": msg["indisponivel"]}, status=503)

    registro.resposta = r["resposta"]
    registro.fontes = r["fontes"]
    registro.modelo = r["modelo"]
    registro.tokens_entrada = r["tokens_entrada"]
    registro.tokens_saida = r["tokens_saida"]
    registro.latencia_ms = int((time.monotonic() - inicio) * 1000)
    registro.save()
    return _resposta_json(registro)


@require_POST
def avaliar_resposta(request):
    """Botoes util/nao util do widget. So vale para respostas do proprio visitante, nas
    ultimas 24h; pode trocar o voto."""
    try:
        dados = json.loads(request.body or b"{}")
        pk, util = int(dados["id"]), dados["util"]
        if not isinstance(util, bool):
            raise ValueError
    except (ValueError, KeyError, TypeError):
        return JsonResponse({"erro": "invalido"}, status=400)
    atualizadas = InteracaoAssistente.objects.filter(
        pk=pk,
        ip_hash=_ip_hash(request),
        criado_em__gte=timezone.now() - timedelta(days=1),
        erro="",
    ).update(util=util)
    if not atualizadas:
        return JsonResponse({"erro": "nao encontrado"}, status=404)
    return JsonResponse({"ok": True})
