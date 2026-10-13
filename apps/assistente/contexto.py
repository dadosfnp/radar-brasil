"""
Contexto do Assistente de Dados: todo o conteudo textual do Radar Brasil
(FAQ da pagina Sobre + fichas tecnicas com criterios avaliados + linhas de
financiamento) como fontes numeradas, para ir inteiro no prompt do modelo.

Cada fonte recebe um ID curto ([P3] = pergunta do FAQ, [F12] = ficha,
[L3] = linha de financiamento) que o modelo cita na resposta; o widget troca o
ID pelo titulo e link da fonte.

Dados do Mapa (Novo PAC por municipio) nao entram aqui: sao tabulares e vao
pela ferramenta consultar_mapa (ferramentas.py).
"""

import html
import re
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.db.models import Max
from django.utils import translation

from apps.indicadores.models import RegistroFicha, RegistroFinanciamento, RegistroMapa
from apps.indicadores.services.avaliacao_painel import get_ficha, get_tabela

_EIXO_LABEL = {
    "pt": {
        "governanca": "Governança",
        "politicas e planos": "Políticas e Planos",
        "programas": "Programas",
        "linhas de financiamento": "Linhas de Financiamento",
    },
    "en": {
        "governanca": "Governance",
        "politicas e planos": "Policies and Plans",
        "programas": "Programs",
        "linhas de financiamento": "Financing Lines",
    },
}

_TXT = {
    "pt": {
        "eixo": "Eixo",
        "criterios": "Avaliação por critério",
        "financiamento": "Linha de financiamento",
        "campos_fin": [
            ("setor", "Setor"),
            ("modalidade", "Modalidade"),
            ("origem", "Origem dos recursos"),
            ("valor", "Valor"),
            ("contrapartida", "Contrapartida"),
            ("federal", "Repasse federal"),
            ("estadual", "Repasse estadual"),
            ("municipal", "Repasse municipal"),
        ],
    },
    "en": {
        "eixo": "Axis",
        "criterios": "Assessment by criterion",
        "financiamento": "Financing line",
        "campos_fin": [
            ("setor", "Sector"),
            ("modalidade", "Modality"),
            ("origem", "Source of funds"),
            ("valor", "Amount"),
            ("contrapartida", "Counterpart"),
            ("federal", "Federal transfer"),
            ("estadual", "State transfer"),
            ("municipal", "Municipal transfer"),
        ],
    },
}


_SOBRE_HTML = Path(settings.BASE_DIR) / "templates" / "municipios" / "sobre.html"
_FAQ_RE = re.compile(
    r'<button class="sb-faq-question"[^>]*>(.*?)</button>\s*'
    r'<div class="sb-faq-answer" hidden>(.*?)</div>',
    re.S,
)
_TRANS_RE = re.compile(r"""{%\s*trans\s+(["'])(.*?)\1\s*%}""", re.S)


def _texto_faq(trecho: str, lang: str) -> str:
    """Trecho do template -> texto puro, com cada {% trans %} traduzido para `lang`."""
    with translation.override(lang):
        s = _TRANS_RE.sub(lambda m: translation.gettext(m.group(2)), trecho)
    s = re.sub(r"<svg.*?</svg>|{%.*?%}", "", s, flags=re.S)
    s = re.sub(r"</p>|</li>|<br\s*/?>", "\n", s)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    return "\n".join(" ".join(linha.split()) for linha in s.splitlines() if linha.strip())


def ler_faq(lang: str = "pt") -> list:
    """[(pergunta, resposta)] do FAQ da pagina Sobre (fonte unica do texto)."""
    trechos = _FAQ_RE.findall(_SOBRE_HTML.read_text(encoding="utf-8"))
    return [(_texto_faq(q, lang), _texto_faq(a, lang)) for q, a in trechos]


def _versao_dados(lang: str) -> tuple:
    """Muda a cada sync_sheets_db (apaga e reinsere, gerando novos IDs) e a cada
    edicao do FAQ no template."""
    f = RegistroFicha.objects.filter(lang=lang).aggregate(m=Max("id"))["m"]
    l_ = RegistroFinanciamento.objects.filter(lang=lang).aggregate(m=Max("id"))["m"]
    return (f, l_, _SOBRE_HTML.stat().st_mtime)


def versao_respostas(lang: str) -> str:
    """Muda sempre que algo que alimenta as respostas muda (contexto + dados do Mapa).
    Respostas guardadas so sao reaproveitadas dentro da mesma versao."""
    mapa = RegistroMapa.objects.filter(lang=lang).aggregate(m=Max("id"))["m"]
    return f"{_versao_dados(lang)}|{mapa}"


def montar_contexto(lang: str = "pt") -> dict:
    """{"texto": str com todas as fontes, "fontes": {id: {titulo, eixo, url}}}."""
    lang = "en" if lang == "en" else "pt"
    return _montar(lang, _versao_dados(lang))


@lru_cache(maxsize=4)
def _montar(lang: str, _versao: tuple) -> dict:
    # ponytail: cache por processo, chaveado pela versao dos dados (no Postgres os IDs
    # nunca se repetem entre syncs; no SQLite de dev podem). Com varios
    # workers cada um monta o seu (~200 consultas leves, uma vez por sync).
    txt = _TXT[lang]
    blocos, fontes = [], {}

    for n, (pergunta, resposta) in enumerate(ler_faq(lang), start=1):
        pid = f"P{n}"
        blocos.append(f"[{pid}] {pergunta}\n{resposta}")
        fontes[pid] = {"titulo": pergunta, "eixo": "FAQ", "url": "/sobre/"}

    fichas = RegistroFicha.objects.filter(lang=lang).order_by("eixo", "estrutura")
    for n, reg in enumerate(fichas, start=1):
        fid = f"F{n}"
        eixo = _EIXO_LABEL[lang].get(reg.eixo, reg.eixo)
        ficha = get_ficha(reg.estrutura, lang)
        linhas = [f"[{fid}] {reg.estrutura}", f"{txt['eixo']}: {eixo}"]
        for campo in ficha.get("campos", []):
            linhas.append(f"{campo['label']}: {campo['valor']}")
        criterios = get_tabela(reg.estrutura, lang)
        if criterios:
            linhas.append(f"{txt['criterios']}:")
            for c in criterios:
                linhas.append(
                    f"- {c['avaliacao']}: {c['nivel']} ({c['criterio']}). {c['descritivo']}".strip()
                )
        blocos.append("\n".join(linhas))
        fontes[fid] = {"titulo": reg.estrutura, "eixo": eixo, "url": ficha.get("link_eixo")}

    for n, reg in enumerate(RegistroFinanciamento.objects.filter(lang=lang), start=1):
        lid = f"L{n}"
        linhas = [f"[{lid}] {txt['financiamento']}: {reg.programa}"]
        for attr, label in txt["campos_fin"]:
            val = (getattr(reg, attr) or "").strip()
            if val:
                linhas.append(f"{label}: {val}")
        blocos.append("\n".join(linhas))
        fontes[lid] = {
            "titulo": reg.programa,
            "eixo": _EIXO_LABEL[lang]["linhas de financiamento"],
            "url": None,
        }

    return {"texto": "\n\n".join(blocos), "fontes": fontes}
