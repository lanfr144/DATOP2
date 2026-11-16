# Correction : fichier manquant (ROOT_URLCONF = "myproject.urls").
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),   # pour toute URL, chercher aussi dans core/urls.py
]
