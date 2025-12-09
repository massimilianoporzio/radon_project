# 🔍 Gestione Dati Mancanti - Comuni Piemonte

## 📊 Situazione Attuale

### Copertura Dati (Analisi: Dicembre 2025)

```
📊 Media Radon:
   ✅ Totale comuni: 1273
   ✅ Con media radon: 1272 (99.9%)
   ⚠️  Senza media radon: 1 (0.1%)

🎯 Area Prioritaria:
   ✅ Totale comuni: 1180
   ✅ Con area prioritaria: 1180 (100.0%)
   ℹ️  93 comuni non presenti nella tabella aree_prioritarie_radon
```

### Comune con Dati Mancanti

- **Moransengo-Tonengo** (Asti): ❌ NO media radon | ❌ NO area prioritaria

______________________________________________________________________

## ✅ Come Vengono Gestiti i Dati Mancanti

### 1. **Database Level (PostgreSQL/PostGIS)**

#### Query API con LEFT JOIN

```sql
SELECT
    m."comune_nom" as nome,
    m."media" as media_radon,
    a."ap" as area_prioritaria,
    ST_AsGeoJSON(...) as geom_json
FROM medie_radon_comunali m
LEFT JOIN aree_prioritarie_radon a
    ON m."comune_ist" = a."comune_ist"
WHERE m.geom IS NOT NULL
```

**Risultato:**

- ✅ LEFT JOIN garantisce che **TUTTI** i comuni vengano restituiti
- ✅ Se manca l'area prioritaria → `area_prioritaria` = `NULL`
- ✅ Se manca la media radon → `media_radon` = `NULL`

### 2. **Backend Level (Django Views)**

#### File: `territorio/views.py`

```python
# Gestione NULL per media_radon
media_radon_formatted = (
    round(media_radon, 1) if media_radon is not None else None
)

# Gestione NULL per area_prioritaria
features.append({
    "properties": {
        "nome": nome,
        "media_radon": media_radon_formatted,  # None se mancante
        "area_prioritaria": area_prioritaria or "N/D",  # "N/D" se NULL
    }
})
```

**Comportamento:**

- ✅ `media_radon`: `None` se mancante → Frontend può verificare con `if (props.media_radon !== null)`
- ✅ `area_prioritaria`: `"N/D"` se NULL → Sempre una stringa, mai undefined

### 3. **Frontend Level (JavaScript - Tooltip)**

#### File: `templates/admin/territorio/comunearpa/change_list.html`

```javascript
// Media Radon con gestione NULL
if (props.media_radon !== null) {
  var radonColor =
    props.media_radon > 300
      ? "#dc2626"
      : props.media_radon > 200
      ? "#f59e0b"
      : "#10b981";
  popupContent +=
    '<span style="background-color: ' +
    radonColor +
    ';">' +
    props.media_radon +
    " Bq/m³</span>";
} else {
  popupContent += "<em>Dato non disponibile</em>";
}

// Area Prioritaria con gestione N/D
if (props.area_prioritaria && props.area_prioritaria !== "N/D") {
  // Mostra classificazione con colori
  var apColor = determineColor(props.area_prioritaria);
  popupContent +=
    '<span style="color: ' +
    apColor +
    ';">' +
    props.area_prioritaria +
    "</span>";
} else {
  popupContent +=
    '<span style="color: #9ca3af; font-style: italic;">' +
    "Dato non disponibile</span>";
}
```

**Visualizzazione nel Tooltip:**

✅ **Comune completo (es. Pinerolo):**

```
🏘️ Pinerolo
Provincia: Torino
Radon medio: 138.5 Bq/m³ [🟠]
Piano Radon: Aree di attenzione [arancione]
```

⚠️ **Comune con dati mancanti (es. Moransengo-Tonengo):**

```
🏘️ Moransengo-Tonengo
Provincia: Asti
Radon medio: Dato non disponibile [grigio corsivo]
Piano Radon: Dato non disponibile [grigio corsivo]
```

### 4. **Admin Level (Django Admin)**

#### File: `territorio/admin.py`

##### Lista Comuni con Indicatori

```python
def media_radon_display(self, obj):
    if obj.media_radon is None:
        return mark_safe('<span style="color: #9ca3af;">N/D</span>')

    # Colorazione basata sul livello
    color = get_radon_color(obj.media_radon)
    return mark_safe(f'<span style="color: {color};">{obj.media_radon:.1f} Bq/m³</span>')
```

##### Filtro Personalizzato "Completezza Dati"

```python
class DatiMissingFilter(admin.SimpleListFilter):
    title = "Completezza Dati"

    def lookups(self, request, model_admin):
        return (
            ("radon_missing", "Senza media radon"),
            ("completi", "Dati completi"),
        )
```

**Funzionalità Admin:**

- ✅ Filtro "Completezza Dati" → Trova rapidamente comuni con dati mancanti
- ✅ Colonna "Radon Medio" → `N/D` in grigio se mancante
- ✅ Indicatori visivi → Colori basati sul livello di rischio

______________________________________________________________________

## 🎨 Design Pattern di Visualizzazione

### Colori Standard per Dati Mancanti

```
N/D → #9ca3af (grigio chiaro)
Stile → font-style: italic
```

### Colori per Media Radon

```
> 300 Bq/m³ → #dc2626 (rosso)
200-300 Bq/m³ → #f59e0b (arancione)
< 200 Bq/m³ → #10b981 (verde)
```

### Colori per Area Prioritaria

```
Aree prioritarie → #dc2626 (rosso)
Aree di attenzione → #f59e0b (arancione)
Aree non prioritarie → #10b981 (verde)
N/D → #9ca3af (grigio)
```

______________________________________________________________________

## 🔧 Estensione Futura per Altri Dati Geologici

Quando aggiungerai **geologia**, **permeabilità**, **faglie**, usa lo stesso pattern:

### Backend (Views)

```python
# LEFT JOIN con tutte le tabelle
sql = """
    SELECT
        m.*,
        a.area_prioritaria,
        g.litologia,
        p.classe_permeabilita
    FROM medie_radon_comunali m
    LEFT JOIN aree_prioritarie_radon a ON ...
    LEFT JOIN zone_geologiche g ON ST_Intersects(m.geom, g.geom)
    LEFT JOIN zone_permeabilita p ON ST_Intersects(m.geom, p.geom)
"""

# Gestione NULL
properties = {
    "geologia": litologia or "N/D",
    "permeabilita": permeabilita or "N/D",
}
```

### Frontend

```javascript
if (props.geologia && props.geologia !== "N/D") {
  // Mostra dato geologico
} else {
  popupContent += "<em>Dato non disponibile</em>";
}
```

______________________________________________________________________

## 📋 Checklist Pre-Deploy

Prima di mettere in produzione, verifica:

- \[ \] ✅ LEFT JOIN usato per tutte le tabelle opzionali
- \[ \] ✅ Backend gestisce `NULL` → converte in `None` o `"N/D"`
- \[ \] ✅ Frontend verifica `!== null` e `!== 'N/D'`
- \[ \] ✅ Stile visivo consistente per dati mancanti (grigio + corsivo)
- \[ \] ✅ Filtri admin per trovare comuni con dati incompleti
- \[ \] ✅ Messaggio utente chiaro: "Dato non disponibile" (non errori criptici)
- \[ \] ✅ Log dei comuni con dati mancanti per successive integrazioni

______________________________________________________________________

## 🐛 Troubleshooting

### Problema: Tooltip non si carica

**Causa:** JavaScript riceve `undefined` invece di `null`
**Soluzione:** Backend deve sempre restituire `null` o `"N/D"`, mai omettere il campo

### Problema: Comuni scompaiono dalla mappa

**Causa:** INNER JOIN invece di LEFT JOIN
**Soluzione:** Usa sempre LEFT JOIN per dati opzionali

### Problema: Errore "Cannot read property of null"

**Causa:** Frontend non controlla `!== null` prima di usare il dato
**Soluzione:** Aggiungi sempre controllo: `if (props.campo !== null && props.campo !== 'N/D')`

______________________________________________________________________

## 📈 Monitoraggio Dati Mancanti

### Query SQL per Report

```sql
-- Trova tutti i comuni con almeno un dato mancante
SELECT
    m."comune_nom" as nome,
    m."provin_nom" as provincia,
    CASE WHEN m."media" IS NULL THEN '❌' ELSE '✅' END as ha_radon,
    CASE WHEN a."ap" IS NULL THEN '❌' ELSE '✅' END as ha_area_prioritaria
FROM medie_radon_comunali m
LEFT JOIN aree_prioritarie_radon a
    ON m."comune_ist" = a."comune_ist"
WHERE m."media" IS NULL
   OR a."ap" IS NULL
ORDER BY provincia, nome;
```

### Script Python per Audit

```python
# check_data_completeness.py
from territorio.models import ComuneArpa

comuni_incompleti = ComuneArpa.objects.filter(media_radon__isnull=True)
print(f"⚠️ {comuni_incompleti.count()} comuni senza media radon")
```

______________________________________________________________________

**Conclusione:** La gestione dei dati mancanti è **robusta e fail-safe** a tutti i livelli dello stack. Il sistema degrada gracefully mostrando "N/D" invece di generare errori. ✅
