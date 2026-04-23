from django.urls import path
from . import views

app_name = "indicadores"

urlpatterns = [
    path("painel-multinivel/", views.painel_multinivel_view, name="painel_multinivel"),
    path("api/painel-multinivel/", views.api_painel_multinivel, name="painel_multinivel_api"),
]