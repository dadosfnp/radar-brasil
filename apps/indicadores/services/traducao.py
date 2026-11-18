"""
Tradução PT -> EN/ES via Gemini — uso exclusivo do comando sync_sheets_db.
Fichas e Parâmetros deixaram de ter planilha EN própria (2026-11-18): a equipe de dados
mantém só o PT e este módulo gera EN/ES a partir dele, com cache em TraducaoCache pra não
retraduzir texto que não mudou entre uma importação e outra.

Campos que NUNCA passam por aqui (ficam iguais em qualquer idioma): eixo (chave normalizada
PT), nível ("Nível N" canônico), links, e os nomes de critério/avaliação — esses usam
CRITERIO_EN/CRITERIO_ES (vocabulário fixo, só 12 valores) em vez de tradução livre, pra nunca
divergir do que painel_multinivel.py já espera encontrar.
"""

import hashlib
import json
import logging
import os
import time

from django.db import transaction
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# "gemini-3-flash" (usado como 3a reserva no Assistente) nao existe na API — 404 sempre;
# confirmado em 2026-11-18 via client.models.list(). Aqui a 3a reserva e gemini-3.5-flash-lite,
# que existe de verdade e tem cota propria. Ordem com gemini-3.1-flash-lite primeiro porque,
# em 2026-11-18, gemini-3.5-flash estourou a cota gratuita diaria (20/dia) nos testes desta
# sessao — tentar ele primeiro so desperdicava uma chamada com 429 instantaneo em todo lote.
_PADRAO_MODELOS = "gemini-3.1-flash-lite,gemini-3.5-flash-lite,gemini-3.5-flash"
TAMANHO_LOTE = 40  # textos por chamada — equilibra nº de chamadas x risco de JSON truncado

# Vocabulário fixo dos 12 nomes de critério/avaliação (ver painel_multinivel._EN_CRITERIO).
# Tradução literal teria risco de o Gemini usar uma palavra diferente da já consolidada
# no restante do código — aqui é sempre a mesma string exata.
CRITERIO_EN = {
    "Operacionalidade": "Operability",
    "Espaço de diálogo federativo": "Federative dialogue space",
    "Comunicação e Transparência": "Communication and Transparency",
    "Financiamento": "Financing",
    "Representação de Gênero, Raça e Etnia": "Representation of Gender, Race and Ethnicity",
    "Cooperação Federativa": "Federative Cooperation",
    "Capilaridade e Alcance Territorial": "Capillarity and Territorial Reach",
    "Fortalecimento da Capacidade Local": "Strengthening Local Capacity",
    "Monitoramento e Participação Local": "Monitoring and Local Participation",
    "Desenho Participativo da Linha de Financiamento": (
        "Participatory Design of the Financing Line"
    ),
    "Capacidade de Execução Descentralizada": "Decentralized Execution Capability",
    "Monitoramento e Prestação de Contas": "Monitoring and Accountability",
}

CRITERIO_ES = {
    "Operacionalidade": "Operatividad",
    "Espaço de diálogo federativo": "Espacio de diálogo federativo",
    "Comunicação e Transparência": "Comunicación y Transparencia",
    "Financiamento": "Financiamiento",
    "Representação de Gênero, Raça e Etnia": "Representación de Género, Raza y Etnia",
    "Cooperação Federativa": "Cooperación Federativa",
    "Capilaridade e Alcance Territorial": "Capilaridad y Alcance Territorial",
    "Fortalecimento da Capacidade Local": "Fortalecimiento de la Capacidad Local",
    "Monitoramento e Participação Local": "Monitoreo y Participación Local",
    "Desenho Participativo da Linha de Financiamento": (
        "Diseño Participativo de la Línea de Financiamiento"
    ),
    "Capacidade de Execução Descentralizada": "Capacidad de Ejecución Descentralizada",
    "Monitoramento e Prestação de Contas": "Monitoreo y Rendición de Cuentas",
}

_NOME_IDIOMA = {"en": "English", "es": "Spanish (Spain)"}


class TraducaoIndisponivel(Exception):
    """Gemini sem chave configurada ou todos os modelos de reserva falharam."""


def _hash(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _modelos() -> list:
    # Variavel propria (nao GEMINI_MODELS, que e do Assistente) — listas de fallback
    # diferentes podem fazer sentido pros dois usos, e um .env que ja define GEMINI_MODELS
    # nao deve sobrescrever silenciosamente a lista daqui.
    bruto = os.environ.get("GEMINI_TRADUCAO_MODELS", _PADRAO_MODELOS)
    return [m.strip() for m in bruto.split(",") if m.strip()]


def _cliente():
    chave = os.environ.get("GEMINI_API_KEY")
    if not chave:
        raise TraducaoIndisponivel("GEMINI_API_KEY nao configurada")
    # Timeout proprio (nao usa GEMINI_TIMEOUT_S do Assistente, que e curto de proposito
    # pra nao travar o chat) — sync roda offline e pode esperar mais por um lote maior.
    timeout_s = int(os.environ.get("GEMINI_TRADUCAO_TIMEOUT_S", "60"))
    return genai.Client(
        api_key=chave,
        http_options=types.HttpOptions(timeout=timeout_s * 1000),
    )


def _extrair_json(texto) -> dict:
    """Gemini às vezes envolve a resposta em ```json ... ``` — remove antes de dar parse.
    `texto` pode vir None (resposta sem parte de texto — bloqueio de segurança, etc.)."""
    if not texto:
        raise ValueError("resposta do Gemini sem texto (bloqueada ou vazia)")
    t = texto.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        if t.endswith("```"):
            t = t[:-3]
        if t.lower().startswith("json"):
            t = t[4:]
    return json.loads(t.strip())


def _traduzir_lote_gemini(client, modelo: str, textos: list, lang: str) -> dict:
    """Uma chamada ao Gemini traduzindo até TAMANHO_LOTE textos de uma vez.
    Retorna {indice_str: traducao}; lança em caso de erro de API ou JSON invalido."""
    idioma = _NOME_IDIOMA[lang]
    payload = {str(i): t for i, t in enumerate(textos)}
    instrucao = (
        f"Traduza cada valor deste objeto JSON de Português do Brasil para {idioma}. "
        "Mantenha o mesmo conjunto de chaves, na mesma ordem, uma tradução por chave. "
        "Traduza normalmente nomes de atos normativos (ex.: 'Decreto nº' -> 'Decree No.', "
        "'Lei nº' -> 'Law No.'), preservando apenas os números/códigos de identificação "
        "e as URLs exatamente como estão. "
        "Responda APENAS com um objeto JSON válido, sem comentários, sem markdown, "
        'no mesmo formato {"0": "...", "1": "..."}.\n\n'
        f"{json.dumps(payload, ensure_ascii=False)}"
    )
    resp = client.models.generate_content(model=modelo, contents=instrucao)
    dados = _extrair_json(resp.text)
    if set(dados.keys()) != set(payload.keys()):
        raise ValueError(f"Gemini devolveu {len(dados)} chaves, esperava {len(payload)}")
    return dados


def traduzir_textos(textos, lang: str) -> dict:
    """Traduz um conjunto de textos PT únicos para `lang` ("en"/"es"), usando o cache
    sempre que possível. Retorna {texto_pt: texto_traduzido}. Nunca lança por falha do
    Gemini — na pior hipótese, devolve o próprio texto em PT pra não travar o sync."""
    from apps.indicadores.models import TraducaoCache

    unicos = sorted({t.strip() for t in textos if t and t.strip()})
    if not unicos:
        return {}

    resultado = {}
    hashes = {_hash(t): t for t in unicos}
    existentes = TraducaoCache.objects.filter(hash_origem__in=hashes.keys(), lang=lang)
    for c in existentes:
        resultado[hashes[c.hash_origem]] = c.texto_traduzido

    faltando = [t for t in unicos if t not in resultado]
    if not faltando:
        return resultado

    try:
        client = _cliente()
    except TraducaoIndisponivel:
        logger.warning("Traducao indisponivel (sem GEMINI_API_KEY) — usando texto em PT")
        for t in faltando:
            resultado[t] = t
        return resultado

    modelos = _modelos()
    novos_para_cache = []
    for inicio in range(0, len(faltando), TAMANHO_LOTE):
        lote = faltando[inicio : inicio + TAMANHO_LOTE]
        traduzido = None
        for modelo in modelos:
            try:
                dados = _traduzir_lote_gemini(client, modelo, lote, lang)
                traduzido = [dados[str(i)] for i in range(len(lote))]
                break
            except Exception as exc:  # noqa: BLE001 — qualquer falha tenta o proximo modelo
                logger.warning("Lote de traducao falhou em %s: %s", modelo, exc)
                time.sleep(1)
        sucesso = traduzido is not None
        if not sucesso:
            logger.error(
                "Nenhum modelo conseguiu traduzir o lote (%d textos) — usando PT", len(lote)
            )
            traduzido = lote
        for original, final in zip(lote, traduzido):
            resultado[original] = final
            # Só entra no cache quando a tradução realmente aconteceu — um fallback pro
            # texto em PT (todos os modelos falharam) não pode "grudar" como se fosse
            # definitivo, senão a próxima tentativa nunca mais chama o Gemini de novo.
            if sucesso:
                novos_para_cache.append(
                    TraducaoCache(
                        hash_origem=_hash(original),
                        lang=lang,
                        texto_pt=original,
                        texto_traduzido=final,
                    )
                )

    if novos_para_cache:
        with transaction.atomic():
            TraducaoCache.objects.bulk_create(
                novos_para_cache, ignore_conflicts=True, batch_size=200
            )

    return resultado
