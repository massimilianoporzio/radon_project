from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from leaflet.admin import LeafletGeoAdmin
from unfold.admin import ModelAdmin

from .models import ComuneArpa


# Custom admin class che combina Unfold e Leaflet
class UnfoldLeafletGeoAdmin(ModelAdmin, LeafletGeoAdmin):
    """
    Admin personalizzata che integra Unfold UI con Leaflet per mappe GIS.
    django-leaflet gestisce automaticamente il widget della mappa nei form.
    """

    # Configurazione Leaflet specifica per questa admin
    settings_overrides = {
        "DEFAULT_CENTER": (45.0, 7.6),
        "DEFAULT_ZOOM": 8,
    }


@admin.register(ComuneArpa)
class ComuneArpaAdmin(UnfoldLeafletGeoAdmin):
    # Template personalizzato per la lista con mappa
    change_list_template = "admin/territorio/comunearpa/change_list.html"

    # Colonne che vedrai nella lista
    list_display = ("nome", "codice_istat", "provincia")

    # Barra di ricerca
    search_fields = ("nome", "codice_istat")

    # IL FILTRO LATERALE (La tua richiesta!)
    list_filter = ("provincia",)

    # Campi da mostrare nel form (incluso la mappa)
    fields = ("codice_istat", "nome", "provincia", "mappa_confini")
    readonly_fields = ("codice_istat", "nome", "provincia", "mappa_confini")

    def mappa_confini(self, obj):
        """Mostra la mappa interattiva del comune"""
        if not obj or not obj.geom:
            return "Nessuna geometria disponibile"

        context = {
            "codice_istat": obj.codice_istat,
            "nome": obj.nome,
            "provincia": obj.provincia,
            "geojson": obj.geom.geojson,
        }
        html = render_to_string("territorio/widgets/readonly_leaflet_widget.html", context)
        return mark_safe(html)

    mappa_confini.short_description = "Mappa Confini Comunali"

    # Disabilitiamo le modifiche (è sola lettura)
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
