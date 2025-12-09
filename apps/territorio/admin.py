from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from leaflet.admin import LeafletGeoAdmin
from unfold.admin import ModelAdmin

from .models import AreaPrioritariaRadon, ComuneArpa, ComuneCompleto
from .utils import (
    RADON_THRESHOLD_HIGH,
    RADON_THRESHOLD_MEDIUM,
    get_area_prioritaria_badge_class,
)


# Filtri personalizzati per dati mancanti
class DatiMissingFilter(admin.SimpleListFilter):
    """Filtro per comuni con dati mancanti"""

    title = "Completezza Dati"
    parameter_name = "dati_missing"

    def lookups(self, request, model_admin):
        return (
            ("radon_missing", "Senza media radon"),
            ("completi", "Dati completi"),
        )

    def queryset(self, request, queryset):
        if self.value() == "radon_missing":
            return queryset.filter(media_radon__isnull=True)
        if self.value() == "completi":
            return queryset.filter(media_radon__isnull=False)
        return queryset


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

    def changelist_view(self, request, extra_context=None):
        """Override per iniettare le soglie radon e l'URL base admin nel template JavaScript."""
        extra_context = extra_context or {}

        # URL base per i dettagli comuni (es: /secret-admin/territorio/comunearpa/)
        admin_base_url = request.path.rstrip("/")

        extra_context.update(
            {
                "radon_threshold_high": RADON_THRESHOLD_HIGH,
                "radon_threshold_medium": RADON_THRESHOLD_MEDIUM,
                "admin_base_url": admin_base_url,
            }
        )
        return super().changelist_view(request, extra_context)

    change_form_template = "admin/territorio/comunearpa/change_form.html"

    # Colonne che vedrai nella lista
    list_display = ("nome", "codice_istat", "provincia", "media_radon_display")

    # Barra di ricerca
    search_fields = ("nome", "codice_istat")

    # Filtri laterali
    list_filter = ("provincia", DatiMissingFilter)

    # Preserva i filtri quando si naviga tra le pagine
    preserve_filters = True

    # Campi da mostrare nel form con layout a 2 colonne
    fieldsets = (
        (
            None,
            {
                "fields": (("codice_istat", "nome", "provincia"),),
                "classes": ("tab",),  # Prima tab: informazioni base compatte
            },
        ),
        (
            "Mappa e Dati Radon",
            {
                "fields": (
                    "mappa_confini",
                    ("media_radon", "area_prioritaria_display"),
                ),
                "description": "Visualizzazione geografica e livelli di concentrazione radon",
                "classes": ("wide",),  # Layout largo per sfruttare spazio
            },
        ),
        (
            "Dati Geologici",
            {
                "fields": ("dati_geologici_display",),
                "description": "Caratterizzazione geologica del territorio comunale",
                "classes": ("collapse", "wide"),  # Collassabile e largo
            },
        ),
    )

    readonly_fields = (
        "codice_istat",
        "nome",
        "provincia",
        "media_radon",
        "area_prioritaria_display",
        "dati_geologici_display",
        "mappa_confini",
    )

    def get_object(self, request, object_id, from_field=None):
        """
        Override per pre-caricare i dati completi dal modello ComuneCompleto.

        Side Effects:
            Imposta l'attributo `_cached_comune_completo` sull'oggetto ComuneArpa recuperato.
            Questo cache viene poi riutilizzato dai metodi display (area_prioritaria_display,
            dati_geologici_display) per evitare query duplicate alla VIEW comuni_completi.

        Returns:
            ComuneArpa: L'oggetto richiesto con il cache _cached_comune_completo impostato.
        """
        obj = super().get_object(request, object_id, from_field)
        if obj:
            # Carica subito i dati completi e li mette in cache sull'oggetto
            try:
                obj._cached_comune_completo = ComuneCompleto.objects.get(codice_istat=obj.codice_istat)
            except ComuneCompleto.DoesNotExist:
                obj._cached_comune_completo = None
        return obj

    def area_prioritaria_display(self, obj):
        """Mostra l'area prioritaria dal modello ComuneCompleto (usa cache)"""
        comune_completo = getattr(obj, "_cached_comune_completo", None)
        if not comune_completo:
            try:
                comune_completo = ComuneCompleto.objects.get(codice_istat=obj.codice_istat)
            except ComuneCompleto.DoesNotExist:
                comune_completo = None

        ap = comune_completo.area_prioritaria if comune_completo else None

        # Determina il colore del badge usando la utility condivisa
        badge_class = get_area_prioritaria_badge_class(ap)

        context = {"area_prioritaria": ap, "badge_class": badge_class}
        return mark_safe(render_to_string("territorio/admin/area_prioritaria_badge.html", context))

    area_prioritaria_display.short_description = "Area Prioritaria Piano Radon"

    def dati_geologici_display(self, obj):
        """Mostra tutti i dati geologici dalla VIEW comuni_completi (usa cache)"""
        comune_completo = getattr(obj, "_cached_comune_completo", None)
        if not comune_completo:
            try:
                comune_completo = ComuneCompleto.objects.get(codice_istat=obj.codice_istat)
            except ComuneCompleto.DoesNotExist:
                comune_completo = None

        # Verifica se ci sono dati da mostrare
        has_data = False
        if comune_completo:
            has_data = (
                comune_completo.unita_litologica
                or comune_completo.litologia
                or comune_completo.classe_permeabilita
                or comune_completo.distanza_faglia_m is not None
            )

        context = {"comune_completo": comune_completo, "has_data": has_data}
        return mark_safe(render_to_string("territorio/admin/dati_geologici_display.html", context))

    dati_geologici_display.short_description = "Informazioni Geologiche"

    def media_radon_display(self, obj):
        """Formattazione della media radon con colori"""
        if obj.media_radon is None:
            return mark_safe('<span style="color: #9ca3af;">N/D</span>')

        # Colori basati sui livelli di concentrazione (soglie centralizzate)
        if obj.media_radon > RADON_THRESHOLD_HIGH:
            color = "#dc2626"  # rosso
        elif obj.media_radon > RADON_THRESHOLD_MEDIUM:
            color = "#f59e0b"  # arancione
        else:
            color = "#10b981"  # verde

        return mark_safe(f'<span style="color: {color}; font-weight: bold;">{obj.media_radon:.1f} Bq/m³</span>')

    def classe_permeabilita_display(self, obj):
        """Formattazione della classe di permeabilità"""
        if obj.classe_permeabilita is None:
            return mark_safe('<span style="color: #9ca3af;">N/D</span>')

        classi = {
            1: ("Alta", "#10b981"),
            2: ("Media", "#fcd34d"),
            3: ("Bassa", "#f59e0b"),
            4: ("Molto Bassa", "#dc2626"),
        }

        label, color = classi.get(obj.classe_permeabilita, ("Sconosciuta", "#6b7280"))

        return mark_safe(f'<span style="color: {color}; font-weight: bold;">{label} ({obj.classe_permeabilita})</span>')

    classe_permeabilita_display.short_description = "Classe Permeabilità"

    media_radon_display.short_description = "Radon Medio"

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


@admin.register(AreaPrioritariaRadon)
class AreaPrioritariaRadonAdmin(UnfoldLeafletGeoAdmin):
    """Admin per le aree prioritarie secondo il Piano Radon."""

    list_display = ("nome", "codice_istat", "provincia", "area_prioritaria_display")
    search_fields = ("nome", "codice_istat")
    list_filter = ("provincia", "area_prioritaria")

    fields = ("codice_istat", "nome", "provincia", "area_prioritaria", "mappa_confini")
    readonly_fields = ("codice_istat", "nome", "provincia", "area_prioritaria", "mappa_confini")

    def area_prioritaria_display(self, obj):
        """Formattazione dell'area prioritaria con badge colorato"""
        if not obj.area_prioritaria or obj.area_prioritaria == "N/D":
            return format_html('<span class="text-gray-400 dark:text-gray-500 italic">{}</span>', "Non disponibile")

        # Badge con Tailwind CSS usando la utility condivisa
        badge_class = get_area_prioritaria_badge_class(obj.area_prioritaria)

        return format_html('<span class="px-2 py-1 rounded text-xs font-bold {}">{}</span>', badge_class, obj.area_prioritaria)

    area_prioritaria_display.short_description = "Piano Radon"

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
