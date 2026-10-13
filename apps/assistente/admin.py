from django.contrib import admin

from apps.assistente.models import InteracaoAssistente


@admin.register(InteracaoAssistente)
class InteracaoAssistenteAdmin(admin.ModelAdmin):
    """Revisao das conversas pela equipe: perguntas reais, respostas, fontes e feedback.
    So leitura (trilha de auditoria); apagar continua permitido."""

    list_display = ("criado_em", "lang", "resumo_pergunta", "util", "em_cache", "modelo", "erro")
    list_filter = ("util", "em_cache", "lang", "modelo", ("erro", admin.EmptyFieldListFilter))
    search_fields = ("pergunta", "resposta")
    date_hierarchy = "criado_em"
    ordering = ("-criado_em",)

    def resumo_pergunta(self, obj):
        return obj.pergunta[:90]

    resumo_pergunta.short_description = "Pergunta"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
