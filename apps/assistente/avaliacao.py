"""
Avaliacao do Assistente contra um golden set (comando avaliar_assistente).

Casos: as perguntas do FAQ da pagina Sobre (fonte esperada = a propria pergunta)
+ golden_set.json (perguntas da equipe de especialistas). Cada resposta passa por:
- respondeu sem erro;
- citou a fonte esperada (ou recusou, quando o caso pede recusa);
- todo numero da resposta existe nos dados (contexto ou retorno de consultar_mapa).
  Numero sem lastro = possivel alucinacao.
"""

import json
import re
from pathlib import Path

from apps.assistente.contexto import ler_faq

GOLDEN_SET = Path(__file__).with_name("golden_set.json")

_ESCALA = {
    "mil": 1e3,
    "thousand": 1e3,
    "milhão": 1e6,
    "milhões": 1e6,
    "million": 1e6,
    "millions": 1e6,
    "bilhão": 1e9,
    "bilhões": 1e9,
    "billion": 1e9,
    "billions": 1e9,
}
_NUMERO = re.compile(
    r"(\d+(?:[.,]\d+)*)(?:\s*(mil|milhão|milhões|thousand|millions?|bilhão|bilhões|billions?)\b)?",
    re.I,
)
_CITACAO = re.compile(r"\[(?:[PFLS]\d+|MAPA)(?:\s*[,;]\s*(?:[PFLS]\d+|MAPA))*\]")


def _leituras(bruto: str) -> set:
    """(valor, casas decimais) possiveis de um numero escrito, sem saber se ',' e '.'
    sao separador decimal ou de milhar."""
    leituras = {(float(re.sub(r"[.,]", "", bruto)), 0)}
    for decimal, milhar in ((",", "."), (".", ",")):
        texto = bruto.replace(milhar, "")
        if texto.count(decimal) <= 1:
            casas = len(texto.split(decimal)[1]) if decimal in texto else 0
            leituras.add((float(texto.replace(decimal, ".")), casas))
    return leituras


def numeros(texto: str) -> list:
    """[(trecho como escrito, {(valor, tolerancia de arredondamento)})] por numero."""
    achados = []
    for m in _NUMERO.finditer(_CITACAO.sub(" ", texto)):
        fator = _ESCALA.get((m.group(2) or "").lower(), 1)
        # "724,6 milhões" = valor arredondado: aceita +-0,05 milhao do valor real
        leituras = {(v * fator, 0.5 * 10**-casas * fator) for v, casas in _leituras(m.group(1))}
        achados.append((m.group(0).strip(), leituras))
    return achados


def numeros_sem_lastro(resposta: str, dados: str) -> list:
    """Numeros da resposta que nao aparecem nos dados, aceitando o arredondamento que a
    forma escrita implica ("R$ 724,6 milhões" contra 724603778)."""
    base = {v for _, leituras in numeros(dados) for v, _ in leituras}
    sem_lastro = []
    for trecho, leituras in numeros(resposta):
        if not any(abs(v - b) <= tol for v, tol in leituras for b in base):
            sem_lastro.append(trecho)
    return sem_lastro


def carregar_casos(lang: str = "pt") -> list:
    """FAQ (sempre) + golden_set.json no idioma pedido."""
    casos = [
        {"pergunta": pergunta, "fonte_esperada": pergunta, "origem": "FAQ"}
        for pergunta, _ in ler_faq(lang)
    ]
    if GOLDEN_SET.exists():
        for caso in json.loads(GOLDEN_SET.read_text(encoding="utf-8")):
            if caso.get("lang", "pt") == lang:
                casos.append({**caso, "origem": caso.get("origem", "golden_set")})
    return casos


def avaliar(caso: dict, resultado: dict, contexto_texto: str) -> dict:
    """Pontua uma resposta. `resultado` e o retorno de servico.responder()."""
    fontes = resultado.get("fontes", [])
    if caso.get("recusar"):
        fonte_ok = not fontes
    else:
        esperada = (caso.get("fonte_esperada") or "").casefold()
        fonte_ok = any(
            f["id"].casefold() == esperada or esperada in f["titulo"].casefold() for f in fontes
        )
    dados = contexto_texto + json.dumps(
        resultado.get("dados_ferramentas", []), ensure_ascii=False, default=str
    )
    sem_lastro = numeros_sem_lastro(resultado.get("resposta", ""), dados)
    return {
        "fonte_ok": fonte_ok,
        "numeros_sem_lastro": sem_lastro,
        "aprovado": fonte_ok and not sem_lastro,
    }
