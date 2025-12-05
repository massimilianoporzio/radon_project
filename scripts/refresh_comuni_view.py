"""
Script per aggiornare la VIEW comuni_completi con la versione ottimizzata.
Usa LATERAL JOIN per migliorare le performance del calcolo faglia più vicina.
"""

import os
import sys
from pathlib import Path

import django
from django.db import connection

# Aggiungi il progetto al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

SQL_VIEW = """
CREATE OR REPLACE VIEW comuni_completi AS
SELECT DISTINCT ON (c."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist")
    c."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist" as codice_istat,
    c."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_nom" as nome,
    c."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.provin_nom" as provincia,
    c."esri_geodatabase.geoportale.rad_18_tab_comuni_radon.media" as media_radon,
    c.geom,
    -- Area prioritaria
    ap."esri_geodatabase.geoportale.rad_18_tab_comuni_radon.ap" as area_prioritaria,
    -- Dati geologici (prende la zona più rappresentativa per il comune)
    zg.litho_unit as unita_litologica,
    zg.lithology as litologia,
    zg.age as eta_geologica,
    zg.descript as descrizione_geologica,
    zg.domain as dominio_geologico,
    -- Permeabilità (gridcode: 1=alta, 2=media, 3=bassa, 4=molto bassa)
    zp.gridcode as classe_permeabilita,
    -- Faglia più vicina (distanza in metri e tipo)
    -- LATERAL JOIN ottimizzato: usa indice spaziale GIST invece di scansione completa
    faglia_vicina.distanza_faglia_m,
    faglia_vicina.tipo_faglia_vicina
FROM
    medie_radon_comunali c
LEFT JOIN aree_prioritarie_radon ap ON (
    c."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist" =
    ap."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist"
)
LEFT JOIN
    zone_geologiche zg
    ON ST_Intersects(c.geom, zg.geom)
LEFT JOIN
    zone_permeabilita zp
    ON ST_Intersects(c.geom, zp.geom)
LEFT JOIN LATERAL (
    -- Trova la faglia più vicina sfruttando l'indice spaziale
    SELECT
        ST_Distance(c.geom::geography, zf.geom::geography)
            as distanza_faglia_m,
        zf.tipo as tipo_faglia_vicina
    FROM zone_faglie zf
    ORDER BY c.geom <-> zf.geom  -- Operatore KNN: usa indice GIST
    LIMIT 1
) faglia_vicina ON true
ORDER BY c."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist",
         ST_Area(ST_Intersection(c.geom, zg.geom)) DESC NULLS LAST
;
"""

if __name__ == "__main__":
    print("🔄 Aggiornamento VIEW comuni_completi con query ottimizzata...")

    with connection.cursor() as cursor:
        cursor.execute(SQL_VIEW)

    print("✅ VIEW comuni_completi aggiornata con successo!")
    print("📊 Performance: LATERAL JOIN + indice GIST per calcolo faglia più vicina")

    # Verifica che la VIEW funzioni
    from territorio.models import ComuneCompleto

    count = ComuneCompleto.objects.count()
    print(f"✅ Verifica: {count} comuni trovati nella VIEW")
