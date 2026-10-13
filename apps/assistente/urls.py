from django.urls import path

from . import views

app_name = "assistente"

urlpatterns = [
    path("api/perguntar/", views.perguntar, name="perguntar"),
    path("api/avaliar/", views.avaliar_resposta, name="avaliar"),
]
