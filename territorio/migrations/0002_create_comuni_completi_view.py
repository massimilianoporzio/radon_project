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
        # Crea le tabelle di supporto (necessarie sia in produzione che in test)
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS medie_radon_comunali (
                "esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist" VARCHAR(6),
                "esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_nom" VARCHAR(100),
                "esri_geodatabase.geoportale.lim_01_comuni_in_vigore.provin_nom" VARCHAR(100),
                "esri_geodatabase.geoportale.rad_18_tab_comuni_radon.media" FLOAT,
                geom GEOMETRY(MULTIPOLYGON, 4326)
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS medie_radon_comuni CASCADE;",
        ),
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS aree_prioritarie_radon (
                "esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist" VARCHAR(6),
                "esri_geodatabase.geoportale.rad_18_tab_comuni_radon.ap" VARCHAR(100)
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS aree_prioritarie_radon CASCADE;",
        ),
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS zone_geologiche (
                id SERIAL PRIMARY KEY,
                litho_unit VARCHAR(100),
                lithology VARCHAR(100),
                age VARCHAR(100),
                descript VARCHAR(255),
                domain VARCHAR(100),
                geom GEOMETRY(POLYGON, 4326)
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS zone_geologiche CASCADE;",
        ),
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS zone_permeabilita (
                id SERIAL PRIMARY KEY,
                gridcode INT,
                geom GEOMETRY(POLYGON, 4326)
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS zone_permeabilita CASCADE;",
        ),
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS zone_faglie (
                id SERIAL PRIMARY KEY,
                tipo VARCHAR(100),
                geom GEOMETRY(LINESTRING, 4326)
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS zone_faglie CASCADE;",
        ),
        # Crea la view DOPO le tabelle
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
                -- Faglia più vicina (distanza in metri e tipo)
                -- LATERAL JOIN ottimizzato: usa indice spaziale GIST invece di scansione completa
                faglia_vicina.distanza_faglia_m,
                faglia_vicina.tipo_faglia_vicina
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
            LEFT JOIN LATERAL (
                -- Trova la faglia più vicina sfruttando l'indice spaziale
                SELECT
                    ST_Distance(c.geom::geography, zf.geom::geography) as distanza_faglia_m,
                    zf.tipo as tipo_faglia_vicina
                FROM zone_faglie zf
                ORDER BY c.geom <-> zf.geom  -- Operatore KNN: usa indice GIST
                LIMIT 1
            ) faglia_vicina ON true
            ORDER BY c."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist", ST_Area(ST_Intersection(c.geom, zg.geom)) DESC NULLS LAST
            ;
            """,
            reverse_sql="DROP VIEW IF EXISTS comuni_completi;",
        ),
    ]
