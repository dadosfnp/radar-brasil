"""
Contexto do Assistente de Dados: todo o conteudo textual do Radar Brasil
(FAQ da pagina Sobre + textos das paginas institucionais + fichas tecnicas com
criterios avaliados + linhas de financiamento) como fontes numeradas, para ir
inteiro no prompt do modelo.

Cada fonte recebe um ID curto ([P3] = pergunta do FAQ, [S4] = secao de pagina,
[F12] = ficha, [L3] = linha de financiamento) que o modelo cita na resposta; o
widget troca o ID pelo titulo e link da fonte.

Dados do Mapa (Novo PAC por municipio) nao entram aqui: sao tabulares e vao
pela ferramenta consultar_mapa (ferramentas.py).
"""

import html
import re
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path

from django.conf import settings
from django.db.models import Max
from django.template.loader import render_to_string
from django.urls import reverse
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


_PAGINA = {"pt": "Página", "en": "Page"}

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


# Paginas institucionais que viram fontes [S..]: (template, rota, nome por idioma).
# O texto vem do template renderizado, entao editar a pagina atualiza o assistente.
PAGINAS = [
    (
        "municipios/nota-pais.html",
        "indicadores:nota_pais",
        {"pt": "Nível País", "en": "Country Level"},
    ),
    (
        "municipios/metodologia.html",
        "municipios:metodologia",
        {"pt": "Metodologia", "en": "Methodology"},
    ),
    ("municipios/sobre.html", "municipios:sobre", {"pt": "Sobre", "en": "About"}),
    ("municipios/inicio.html", "municipios:inicio", {"pt": "Início", "en": "Home"}),
    ("municipios/landing.html", "municipios:home", {"pt": "Página inicial", "en": "Landing page"}),
]
_TEMPLATES = Path(settings.BASE_DIR) / "templates"
_MO = Path(settings.BASE_DIR) / "locale" / "en" / "LC_MESSAGES" / "django.mo"


class _TextoDaPagina(HTMLParser):
    """HTML renderizado -> [(titulo da secao, texto)], cortando a pagina em cada h1-h3.
    Ignora o que nao e conteudo (menu, rodape, scripts, desenhos, o proprio chat) e o
    FAQ, que ja entra como [P..]."""

    _PULAR = {
        "head",
        "script",
        "style",
        "svg",
        "noscript",
        "header",
        "nav",
        "footer",
        "iframe",
        "form",
    }
    _PULAR_CLASSE = {"sb-faq-section", "rb-skip-link"}
    _TITULOS = {"h1", "h2", "h3"}
    _QUEBRA = {"p", "li", "div", "tr", "br", "h4", "h5", "h6", "section", "table"}
    _CELULA = {"td", "th"}
    _MINIMO = 40  # secao com menos texto que isso e migalha de navegacao, nao conteudo

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.secoes, self._pulando, self._titulo = [], [], None
        self._buf, self._no_titulo = [], False
        self._math = []  # [tag, filhos ja fechados] dentro de <math>, para escrever fracoes

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self._pulando:
            if tag == self._pulando[0]:
                self._pulando.append(tag)
            return
        if (
            tag in self._PULAR
            or a.get("id") == "as-root"
            or self._PULAR_CLASSE & set((a.get("class") or "").split())
        ):
            self._pulando.append(tag)
        elif tag == "math" or self._math:
            self._math.append([tag, 0])
        elif tag in self._TITULOS:
            self._fechar_secao()
            self._no_titulo = True
        elif tag in self._QUEBRA:
            self._buf.append("\n")

    def handle_endtag(self, tag):
        if self._pulando:
            if tag == self._pulando[0]:
                self._pulando.pop()
        elif self._math:
            self._math.pop()
            # <mfrac>numerador denominador</mfrac> vira "numerador / denominador"
            if self._math and self._math[-1][0] == "mfrac":
                self._math[-1][1] += 1
                if self._math[-1][1] == 1:
                    self._buf.append(" / ")
        elif tag in self._TITULOS and self._no_titulo:
            self._titulo = _limpar("".join(self._buf)) or self._titulo
            self._buf, self._no_titulo = [], False
        elif tag in self._CELULA:
            self._buf.append(" | ")
        elif tag in self._QUEBRA:
            self._buf.append("\n")

    def handle_data(self, data):
        # quebra de linha dentro do HTML e so formatacao do template: vira espaco
        if not self._pulando:
            self._buf.append(data.replace("\n", " ").replace("﻿", ""))

    def _fechar_secao(self):
        texto = _limpar("".join(self._buf), linhas=True)
        if len(texto) >= self._MINIMO:
            self.secoes.append((self._titulo, texto))
        self._buf = []

    def close(self):
        super().close()
        self._fechar_secao()


def _limpar(texto: str, linhas: bool = False) -> str:
    partes = (" ".join(linha.split()).strip(" |") for linha in texto.splitlines())
    partes = [p for p in partes if p]
    return "\n".join(partes) if linhas else " ".join(partes)


def ler_paginas(lang: str = "pt") -> list:
    """[(titulo, texto, url)] de cada secao das paginas institucionais, no idioma."""
    secoes = []
    with translation.override("en" if lang == "en" else "pt-br"):
        for template, rota, nome in PAGINAS:
            parser = _TextoDaPagina()
            # token falso so para o {% csrf_token %} do chat nao gerar aviso; o chat e ignorado
            parser.feed(render_to_string(template, {"csrf_token": "-"}))
            parser.close()
            url = reverse(rota)
            for titulo, texto in parser.secoes:
                secoes.append((f"{nome[lang]}: {titulo}" if titulo else nome[lang], texto, url))
    return secoes


def _versao_dados(lang: str) -> tuple:
    """Muda a cada sync_sheets_db (apaga e reinsere, gerando novos IDs), a cada
    edicao das paginas (FAQ incluido) e a cada traducao compilada."""
    f = RegistroFicha.objects.filter(lang=lang).aggregate(m=Max("id"))["m"]
    l_ = RegistroFinanciamento.objects.filter(lang=lang).aggregate(m=Max("id"))["m"]
    paginas = tuple((_TEMPLATES / t).stat().st_mtime for t, _, _ in PAGINAS)
    mo = _MO.stat().st_mtime if _MO.exists() else 0
    return (f, l_, paginas, mo)


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

    for n, (titulo, texto, url) in enumerate(ler_paginas(lang), start=1):
        sid = f"S{n}"
        blocos.append(f"[{sid}] {titulo}\n{texto}")
        fontes[sid] = {"titulo": titulo, "eixo": _PAGINA[lang], "url": url}

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
