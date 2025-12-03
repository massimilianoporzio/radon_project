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
            default_attrs.update(attrs)
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

    def render(self, name, value, attrs=None, renderer=None):
        """Renderizza il widget in modalità read-only"""
        # Aggiungi classe per nascondere i controlli di editing
        if attrs is None:
            attrs = {}
        attrs["readonly"] = "readonly"
        attrs["style"] = "pointer-events: none; opacity: 0.6;"

        # Renderizza il widget base di Leaflet
        html = super().render(name, value, attrs, renderer)

        # Aggiungi lo script di auto-zoom e read-only dal template
        field_id = attrs.get("id", f"id_{name}")
        script_html = render_to_string(self.template_name, {"id": field_id})

        return html + script_html
