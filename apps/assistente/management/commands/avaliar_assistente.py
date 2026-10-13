"""
Roda o golden set contra o Assistente e mostra um placar.

Uso:
    python manage.py avaliar_assistente                  # FAQ + golden_set.json, em PT
    python manage.py avaliar_assistente --lang en
    python manage.py avaliar_assistente --limite 3       # so os 3 primeiros casos
    python manage.py avaliar_assistente --saida aval.json

Cada caso e uma chamada real ao Gemini (~44 mil tokens): consome cota do plano gratuito.
"""

import json
import time

from django.core.management.base import BaseCommand

from apps.assistente.avaliacao import avaliar, carregar_casos
from apps.assistente.contexto import montar_contexto
from apps.assistente.servico import responder


class Command(BaseCommand):
    help = "Avalia o Assistente com o FAQ + golden_set.json (chamadas reais ao Gemini)."

    def add_arguments(self, parser):
        parser.add_argument("--lang", default="pt", choices=["pt", "en"])
        parser.add_argument("--limite", type=int, default=0, help="Maximo de casos (0 = todos)")
        parser.add_argument(
            "--pausa", type=float, default=5.0, help="Segundos entre perguntas (cota/minuto)"
        )
        parser.add_argument("--saida", default="", help="Salva os resultados neste JSON")

    def handle(self, *args, **opts):
        lang = opts["lang"]
        casos = carregar_casos(lang)
        if opts["limite"]:
            casos = casos[: opts["limite"]]
        contexto = montar_contexto(lang)["texto"]
        resultados = []

        for n, caso in enumerate(casos, start=1):
            if n > 1:
                time.sleep(opts["pausa"])
            inicio = time.monotonic()
            try:
                r = responder(caso["pergunta"], [], lang)
            except Exception as e:  # cota, rede: conta como reprovado, segue
                linha = {**caso, "erro": f"{type(e).__name__}: {e}", "aprovado": False}
            else:
                linha = {
                    **caso,
                    **avaliar(caso, r, contexto),
                    "resposta": r["resposta"],
                    "fontes": [f["id"] for f in r["fontes"]],
                    "modelo": r["modelo"],
                }
            linha["segundos"] = round(time.monotonic() - inicio, 1)
            resultados.append(linha)
            self._imprimir(n, len(casos), linha)

        aprovados = sum(r["aprovado"] for r in resultados)
        erros = sum("erro" in r for r in resultados)
        sem_lastro = sum(bool(r.get("numeros_sem_lastro")) for r in resultados)
        self.stdout.write("")
        estilo = self.style.SUCCESS if aprovados == len(resultados) else self.style.WARNING
        self.stdout.write(
            estilo(
                f"Aprovados: {aprovados}/{len(resultados)} | erros de chamada: {erros} | "
                f"com numero sem lastro: {sem_lastro}"
            )
        )
        if opts["saida"]:
            with open(opts["saida"], "w", encoding="utf-8") as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
            self.stdout.write(f"Resultados salvos em {opts['saida']}")

    def _imprimir(self, n, total, linha):
        marca = self.style.SUCCESS("OK  ") if linha["aprovado"] else self.style.ERROR("FALHA")
        self.stdout.write(f"[{n}/{total}] {marca} {linha['pergunta']} ({linha['segundos']}s)")
        if "erro" in linha:
            self.stdout.write(f"        erro: {linha['erro']}")
            return
        if not linha["fonte_ok"]:
            esperado = "recusa" if linha.get("recusar") else linha.get("fonte_esperada")
            self.stdout.write(f"        fonte: esperado {esperado!r}, citou {linha['fontes']}")
        if linha["numeros_sem_lastro"]:
            self.stdout.write(
                f"        numeros sem lastro nos dados: {linha['numeros_sem_lastro']}"
            )
