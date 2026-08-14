from django.db import models


class RegistroFicha(models.Model):
    """Ficha técnica de uma estrutura por idioma (substitui Google Sheets Fichas PT/EN)."""

    lang = models.CharField(max_length=5)
    estrutura = models.CharField(max_length=500)
    # eixo normalizado: "governanca", "politicas e planos", "programas", "linhas de financiamento"
    eixo = models.CharField(max_length=200, blank=True)
    setor = models.CharField(max_length=200, blank=True)
    link_eixo = models.CharField(max_length=2000, blank=True)
    descricao = models.TextField(blank=True)
    orgao_responsavel = models.TextField(blank=True)
    link_orgao = models.CharField(max_length=2000, blank=True)
    arcabouco_normativo = models.TextField(blank=True)
    link_arcabouco = models.CharField(max_length=2000, blank=True)
    espaco_dialogo_federativo = models.TextField(blank=True)
    financiamento = models.TextField(blank=True)
    periodicidade = models.TextField(blank=True)
    composicao = models.TextField(blank=True)
    carater_decisorio = models.TextField(blank=True)
    politica_plano_relacionado = models.TextField(blank=True)
    contrapartida = models.TextField(blank=True)
    modalidade = models.TextField(blank=True)
    repasse = models.TextField(blank=True)
    fontes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["lang", "estrutura"]),
            models.Index(fields=["lang", "eixo"]),
        ]
        verbose_name = "Ficha Técnica"
        verbose_name_plural = "Fichas Técnicas"

    def __str__(self):
        return f"[{self.lang}] {self.estrutura}"


class RegistroParametro(models.Model):
    """Parâmetros de avaliação multinível por idioma (substitui Google Sheets Parâmetros PT/EN)."""

    lang = models.CharField(max_length=5)
    estrutura = models.CharField(max_length=500)
    # eixo normalizado: "governanca", "politicas e planos", "programas", "linhas de financiamento"
    eixo = models.CharField(max_length=200, blank=True)
    setor = models.CharField(max_length=200, blank=True)
    nivel = models.CharField(max_length=50, blank=True)  # canonical: "Nível 0" … "Nível 5"
    criterio = models.CharField(max_length=500, blank=True)
    avaliacao = models.CharField(max_length=500, blank=True)
    classificacao = models.CharField(max_length=200, blank=True)
    descritivo = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["lang", "estrutura"]),
            models.Index(fields=["lang", "eixo"]),
            models.Index(fields=["lang", "avaliacao", "nivel"]),
        ]
        verbose_name = "Parâmetro"
        verbose_name_plural = "Parâmetros"

    def __str__(self):
        return f"[{self.lang}] {self.estrutura} — {self.avaliacao} — {self.nivel}"


class RegistroFinanciamento(models.Model):
    """Linha de financiamento climático por idioma (substitui Google Sheets Financiamento PT/EN)."""

    lang = models.CharField(max_length=5)
    programa = models.TextField(blank=True)
    setor = models.CharField(max_length=500, blank=True)
    modalidade = models.CharField(max_length=500, blank=True)
    origem = models.CharField(max_length=500, blank=True)
    valor = models.CharField(max_length=500, blank=True)
    contrapartida = models.CharField(max_length=500, blank=True)
    federal = models.CharField(max_length=500, blank=True)
    estadual = models.CharField(max_length=500, blank=True)
    municipal = models.CharField(max_length=500, blank=True)
    ente = models.CharField(max_length=500, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["lang"]),
            models.Index(fields=["lang", "setor"]),
        ]
        verbose_name = "Financiamento Climático"
        verbose_name_plural = "Financiamentos Climáticos"

    def __str__(self):
        return f"[{self.lang}] {self.programa[:60]}"


class RegistroMapa(models.Model):
    """Registro de investimento para o mapa georreferenciado (substitui Google Sheets Mapa)."""

    lang = models.CharField(max_length=5)
    code_muni = models.CharField(max_length=20, blank=True)
    uf = models.CharField(max_length=5, blank=True)
    municipio = models.CharField(max_length=200, blank=True)
    estagio = models.CharField(max_length=200, blank=True)
    perfil = models.CharField(max_length=200, blank=True)
    estimativa_2023_2030 = models.FloatField(default=0.0)
    populacao = models.CharField(max_length=200, blank=True)
    empreendimento = models.CharField(max_length=500, blank=True)
    eixo = models.CharField(max_length=200, blank=True)
    modalidade = models.CharField(max_length=200, blank=True)
    tipo_executor = models.CharField(max_length=200, blank=True)
    percentual_executado = models.FloatField(default=0.0)

    class Meta:
        indexes = [
            models.Index(fields=["lang", "code_muni"]),
            models.Index(fields=["lang", "uf"]),
        ]
        verbose_name = "Registro do Mapa"
        verbose_name_plural = "Registros do Mapa"

    def __str__(self):
        return f"[{self.lang}] {self.municipio} ({self.uf})"
