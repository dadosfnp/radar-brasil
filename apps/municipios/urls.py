from django.urls import path
from . import views

app_name = "municipios"

urlpatterns = [
    path("", views.landing, name="home"),
    path("inicio/", views.inicio, name="inicio"),
    path("metodologia/", views.metodologia, name="metodologia"),
]
