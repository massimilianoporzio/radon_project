# Integrazione Django-Leaflet con Unfold Admin

## Panoramica

Questa integrazione permette di visualizzare dati geografici (geometrie PostGIS) nell'admin di Django usando Leaflet, mantenendo lo stile di Unfold. L'implementazione usa un **readonly field personalizzato** con template dedicato per massima flessibilità e separazione dei compiti.

## Componenti installati

### 1. Pacchetto django-leaflet

- **Versione**: 0.33.0
- **Aggiunto in**: `pyproject.toml`
- **Funzione**: Fornisce configurazione base e assets Leaflet per Django

### 2. Configurazione in settings (base.py)

```python
# App aggiunta
INSTALLED_APPS = [
    ...
    "leaflet",
    ...
]

# Configurazione Leaflet
LEAFLET_CONFIG = {
    "DEFAULT_CENTER": (45.0, 7.6),  # Centro sul Piemonte
    "DEFAULT_ZOOM": 8,
    "MIN_ZOOM": 7,
    "MAX_ZOOM": 18,
    "SCALE": "both",
    "ATTRIBUTION_PREFIX": "Powered by django-leaflet",
    "TILES": [
        (
            "OpenStreetMap",
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                "attribution": '&copy; OpenStreetMap contributors',
                "maxZoom": 19,
            },
        ),
    ],
    "SPATIAL_EXTENT": (6.0, 43.5, 9.5, 46.5),  # Confini Piemonte
    "PLUGINS": {
        "forms": {
            "auto-include": True,
        },
    },
}
```

## Come funziona

### Admin Class (territorio/admin.py)

Classe custom `UnfoldLeafletGeoAdmin` che eredita da `ModelAdmin` (Unfold) e `LeafletGeoAdmin`:

```python
class UnfoldLeafletGeoAdmin(ModelAdmin, LeafletGeoAdmin):
    """Admin personalizzata Unfold + Leaflet."""
    settings_overrides = {
        "DEFAULT_CENTER": (45.0, 7.6),
        "DEFAULT_ZOOM": 8,
    }

@admin.register(ComuneArpa)
class ComuneArpaAdmin(UnfoldLeafletGeoAdmin):
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
        html = render_to_string(
            "territorio/widgets/readonly_leaflet_widget.html", context
        )
        return mark_safe(html)

    mappa_confini.short_description = "Mappa Confini Comunali"
```

### Template (templates/territorio/widgets/readonly_leaflet_widget.html)

Template dedicato che:

- Carica Leaflet CSS e JS
- Crea una mappa standalone con i dati del comune
- Implementa auto-zoom sui confini (maxZoom: 11)
- Aggiunge popup con informazioni del comune
- Usa OpenStreetMap come tile layer

**Vantaggi di questo approccio:**

- ✅ **Separazione dei compiti**: HTML/JS nel template, logica Python nell'admin
- ✅ **Nessun override di template admin**: usa readonly_fields nativi
- ✅ **Facile da personalizzare**: modifica solo il template per cambiare stile/comportamento
- ✅ **Compatibile con Unfold**: integrazione trasparente senza conflitti

## Funzionalità

### Nella pagina di dettaglio del comune:

1. **Mappa interattiva** con il confine del comune evidenziato (blu con bordo scuro)
2. **Auto-zoom automatico** sui confini (maxZoom: 11 per evitare zoom eccessivo)
3. **Popup informativo** con nome, provincia e codice ISTAT
4. **Layer OpenStreetMap** come base
5. **Integrazione perfetta** con Unfold admin (nessun template override necessario)

## Personalizzazioni possibili

### Cambiare lo stile della mappa:

Modifica `readonly_leaflet_widget.html`, sezione `style`:

```javascript
style: {
    fillColor: '#3b82f6',      // Colore riempimento
    weight: 2,                  // Spessore bordo
    opacity: 1,                 // Opacità bordo
    color: '#1e40af',          // Colore bordo
    fillOpacity: 0.3           // Opacità riempimento
}
```

### Cambiare tile layer:

Modifica l'URL del tile layer nel template per usare altri provider:

```javascript
// CartoDB Positron
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', ...)

// CartoDB Dark Matter
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png', ...)

// Esri World Imagery
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', ...)
```

### Personalizzare il popup:

Modifica la sezione `bindPopup` nel template per cambiare contenuto o stile.

## Note importanti

1. **Approccio readonly field**: Usa `readonly_fields` con metodo personalizzato invece di widget form, garantendo compatibilità con `has_change_permission=False`

2. **Read-only**: L'admin è configurata in sola lettura (`has_change_permission=False`), mostra solo il pulsante CHIUDI

3. **Template standalone**: La mappa è completamente indipendente, carica Leaflet autonomamente senza dipendenze dai widget form di django-leaflet

4. **SRID**: Il campo `geom` usa SRID 4326 (WGS84) - standard per coordinate lat/lon

5. **Performance**: Ogni comune ha la sua mappa standalone - ottimale per visualizzazione singola

## File modificati/creati

1. ✅ `pyproject.toml` - Aggiunto `django-leaflet>=0.30.1`
2. ✅ `config/settings/base.py` - Configurazione `LEAFLET_CONFIG` e app in `INSTALLED_APPS`
3. ✅ `territorio/admin.py` - Classe `UnfoldLeafletGeoAdmin` e metodo `mappa_confini()`
4. ✅ `templates/territorio/widgets/readonly_leaflet_widget.html` - Template mappa standalone
5. ✅ `territorio/widgets.py` - (Opzionale, non più usato nella soluzione finale)

## Architettura della soluzione

```
Admin View (territorio/admin.py)
    └── mappa_confini() method
        └── render_to_string()
            └── Template (readonly_leaflet_widget.html)
                ├── Leaflet CSS/JS
                ├── Div mappa
                └── JavaScript inizializzazione
                    ├── Crea mappa
                    ├── Carica GeoJSON
                    ├── Auto-zoom
                    └── Popup
```

## Possibili estensioni future

1. **Heatmap misurazioni radon**: Sovrapponi layer con dati misurazioni
2. **Layer aggiuntivi**: Aggiungi confini regionali, provinciali, ecc.
3. **Clustering**: Per vista lista con molti comuni
4. **Export mappa**: Bottone per esportare la mappa come immagine
5. **Legenda personalizzata**: Aggiungi legenda per colori/simboli
