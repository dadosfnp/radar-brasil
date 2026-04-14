from django.urls import path
from . import views

app_name = "municipios"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("inicio/", views.inicio, name="home"),
]