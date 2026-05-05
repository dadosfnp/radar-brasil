from django.urls import path
from . import views

app_name = "indicadores"

urlpatterns = [
    path("painel-multinivel/", views.painel_multinivel_view, name="painel_multinivel"),
    path("api/painel-multinivel/", views.api_painel_multinivel, name="painel_multinivel_api"),
    path("avaliacao-painel/", views.avaliacao_painel_view, name="avaliacao_painel"),
    path("api/avaliacao/filtros/", views.api_avaliacao_filtros, name="api_avaliacao_filtros"),
    path("api/avaliacao/tabela/", views.api_avaliacao_tabela, name="api_avaliacao_tabela"),
    path("api/avaliacao/ficha/", views.api_avaliacao_ficha, name="api_avaliacao_ficha"),
]