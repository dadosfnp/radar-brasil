from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
import django.conf.urls.i18n as i18n_urls

urlpatterns = [
    path("i18n/", include(i18n_urls)),
    path("admin/", admin.site.urls),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    # Navegadores pedem /favicon.ico na raiz do site automaticamente, por convencao,
    # independente das tags <link rel="icon"> da pagina (achado em 2026-11-18: o
    # icone sumia em paginas especificas mesmo com as tags corretas no <head>).
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/img/favicon.ico", permanent=True),
    ),
    path("", include("apps.municipios.urls")),
    path("indicadores/", include("apps.indicadores.urls")),
    path("assistente/", include("apps.assistente.urls")),
]
