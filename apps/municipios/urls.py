from django.urls import path
from . import views

app_name = "municipios"

urlpatterns = [
    path("", views.inicio, name="home"),
    path("metodologia/", views.metodologia, name="metodologia"),
    path("landing/", views.landing, name="landing"),
]