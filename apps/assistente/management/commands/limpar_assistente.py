"""
Apaga registros antigos do Assistente (politica de retencao, LGPD).

Uso:
    python manage.py limpar_assistente              # usa ASSISTENTE_RETENCAO_DIAS (padrao 90)
    python manage.py limpar_assistente --dias 30
    python manage.py limpar_assistente --simular    # so mostra quantos seriam apagados

Rodar diariamente no droplet (cron do root), por exemplo as 3h:
    0 3 * * * cd /opt/radar-brasil && docker compose exec -T radarbrasil \
        python manage.py limpar_assistente
"""

import os
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.assistente.models import InteracaoAssistente


class Command(BaseCommand):
    help = "Apaga interacoes do Assistente mais antigas que o prazo de retencao."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dias",
            type=int,
            default=int(os.environ.get("ASSISTENTE_RETENCAO_DIAS", "90")),
            help="Prazo de retencao em dias (padrao: ASSISTENTE_RETENCAO_DIAS ou 90)",
        )
        parser.add_argument("--simular", action="store_true", help="Nao apaga, so conta")

    def handle(self, *args, **opts):
        limite = timezone.now() - timedelta(days=opts["dias"])
        antigas = InteracaoAssistente.objects.filter(criado_em__lt=limite)
        if opts["simular"]:
            self.stdout.write(
                f"{antigas.count()} interacoes seriam apagadas (antes de {limite:%d/%m/%Y})."
            )
            return
        apagadas, _ = antigas.delete()
        self.stdout.write(f"{apagadas} interacoes apagadas (antes de {limite:%d/%m/%Y}).")
