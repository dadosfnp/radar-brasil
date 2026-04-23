from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.municipios.urls")),
    path("indicadores/", include("apps.indicadores.urls")),  # ← adiciona esta linha
]