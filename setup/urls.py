from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.i18n import i18n_patterns
import django.conf.urls.i18n as i18n_urls

urlpatterns = [
    path("i18n/", include(i18n_urls)),
    path("admin/", admin.site.urls),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("", include("apps.municipios.urls")),
    path("indicadores/", include("apps.indicadores.urls")),
]
