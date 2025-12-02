from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import ComuneArpa


@admin.register(ComuneArpa)
class ComuneArpaAdmin(ModelAdmin):
    # Colonne che vedrai nella lista
    list_display = ("nome", "codice_istat", "provincia")

    # Barra di ricerca
    search_fields = ("nome", "codice_istat")

    # IL FILTRO LATERALE (La tua richiesta!)
    list_filter = ("provincia",)

    # Disabilitiamo le modifiche (è sola lettura)
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
