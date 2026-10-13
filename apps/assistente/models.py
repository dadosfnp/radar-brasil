from django.db import models


class InteracaoAssistente(models.Model):
    """Uma pergunta ao assistente: trilha de auditoria, base dos limites diarios e
    material para avaliar respostas. Sem IP em claro (LGPD): so um hash com sal."""

    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)
    lang = models.CharField(max_length=5)
    ip_hash = models.CharField(max_length=64, db_index=True)
    pergunta = models.TextField()
    resposta = models.TextField(blank=True)
    fontes = models.JSONField(default=list, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    tokens_entrada = models.PositiveIntegerField(null=True, blank=True)
    tokens_saida = models.PositiveIntegerField(null=True, blank=True)
    latencia_ms = models.PositiveIntegerField(null=True, blank=True)
    erro = models.CharField(max_length=200, blank=True)
    # Reaproveitamento: mesma pergunta (normalizada) + idioma + versao dos dados
    chave_cache = models.CharField(max_length=64, blank=True, db_index=True)
    em_cache = models.BooleanField(default=False)  # resposta reaproveitada, sem chamar a IA
    util = models.BooleanField(null=True, blank=True)  # feedback do visitante (sim/nao)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.criado_em:%Y-%m-%d %H:%M} {self.pergunta[:60]}"
