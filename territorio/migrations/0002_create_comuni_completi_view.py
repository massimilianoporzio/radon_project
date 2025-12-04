"""
Crea una VIEW PostgreSQL che unisce tutte le informazioni sui comuni:
- Dati base comuni (medie_radon_comunali)
- Aree prioritarie (aree_prioritarie_radon)
- Zone geologiche (zone_geologiche) - se disponibile
- Zone permeabilità (zone_permeabilita) - se disponibile
- Zone faglie (zone_faglie) - se disponibile
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('territorio', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
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
                -- Distanza dalla faglia più vicina (in metri)
                (
                    SELECT MIN(ST_Distance(c.geom::geography, zf.geom::geography))
                    FROM zone_faglie zf
                ) as distanza_faglia_m,
                -- Tipo di faglia più vicina
                (
                    SELECT zf.tipo
                    FROM zone_faglie zf
                    ORDER BY ST_Distance(c.geom::geography, zf.geom::geography)
                    LIMIT 1
                ) as tipo_faglia_vicina
            FROM
                medie_radon_comunali c
            LEFT JOIN
                aree_prioritarie_radon ap
                ON c."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist" = ap."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist"
            LEFT JOIN
                zone_geologiche zg
                ON ST_Intersects(c.geom, zg.geom)
            LEFT JOIN
                zone_permeabilita zp
                ON ST_Intersects(c.geom, zp.geom)
            ORDER BY c."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist", ST_Area(ST_Intersection(c.geom, zg.geom)) DESC NULLS LAST
            ;
            """,
            reverse_sql="DROP VIEW IF EXISTS comuni_completi;",
        ),
    ]
