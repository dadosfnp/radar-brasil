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
    path("linha-do-tempo/", views.linha_do_tempo_view, name="linha_do_tempo"),
    path("mapa-georreferenciado/", views.mapa_georreferenciado_view, name="mapa_georreferenciado"),
    path("api/mapa/dados/", views.api_mapa_dados, name="api_mapa_dados"),
    path("api/mapa/filtros/", views.api_mapa_filtros, name="api_mapa_filtros"),
    path("financiamento-climatico/", views.financiamento_climatico_view, name="financiamento_climatico"),
    path("api/financiamento/filtros/", views.api_fin_cli_filtros, name="api_fin_cli_filtros"),
    path("api/financiamento/tabela/", views.api_fin_cli_tabela, name="api_fin_cli_tabela"),
    path("api/financiamento/graficos/", views.api_fin_cli_graficos, name="api_fin_cli_graficos"),
]