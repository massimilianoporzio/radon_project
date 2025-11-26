"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # TRAPPOLA: Chi va su /admin trova il finto login
    path("admin/", include("admin_honeypot.urls", namespace="admin_honeypot")),
    # VERO ADMIN: Tu userai questo indirizzo segreto
    # Puoi cambiarlo in quello che vuoi (es. 'gestione/', 'controllo/', 'super-secret/')
    path("secret-admin/", admin.site.urls),
]
