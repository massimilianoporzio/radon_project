from django.template.loader import render_to_string
from leaflet.forms.widgets import LeafletWidget


class ReadOnlyLeafletWidget(LeafletWidget):
    """
    Widget Leaflet in sola lettura per visualizzare geometrie nella admin.
    """

    template_name = "territorio/widgets/readonly_leaflet_widget.html"

    def __init__(self, attrs=None):
        default_attrs = {
            "map_height": "500px",
            "map_width": "100%",
            "display_raw": False,
            "map_srid": 4326,
        }
        if attrs:
            default_attrs |= attrs
        super().__init__(attrs=default_attrs)

    class Media:
        css = {
            "all": ("leaflet/leaflet.css",),
        }
        js = (
            "leaflet/leaflet.js",
            "leaflet/leaflet.extras.js",
            "leaflet/leaflet.forms.js",
        )

    def render(self, name, value, attrs=None, renderer=None, context=None):
        """Renderizza il widget in modalità read-only"""
        # Aggiungi classe per nascondere i controlli di editing
        if attrs is None:
            attrs = {}
        attrs["readonly"] = "readonly"
        # Use clearer visual indicators similar to disabled fields:
        # reduced opacity, background color change, and disabled cursor
        attrs["style"] = (
            "pointer-events: none; opacity: 0.65; background-color: #f5f5f5; cursor: not-allowed; border-color: #ccc;"
        )

        # Se il contesto è fornito (tramite data-* attrs), usalo per il template
        if context is None:
            context = {}

        # Assicura che il contesto abbia le variabili necessarie
        field_id = attrs.get("id", f"id_{name}")
        context.setdefault("id", field_id)

        # Renderizza il widget base di Leaflet
        html = super().render(name, value, attrs, renderer)

        # Aggiungi lo script di auto-zoom e read-only dal template
        script_html = render_to_string(self.template_name, context)

        return html + script_html
