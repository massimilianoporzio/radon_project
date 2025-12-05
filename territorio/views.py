import json
import logging

from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)


@login_required
def comuni_geojson(request):
    """
    API endpoint che restituisce TUTTI i comuni in formato GeoJSON semplificato.
    Il filtro per provincia viene gestito client-side per evitare ricaricamenti.
    La semplificazione avviene a livello database con PostGIS per performance ottimali.
    """
    # Validate and constrain tolerance parameter to safe range [0.0001, 0.01]
    # This prevents performance issues from excessive simplification values
    try:
        tolerance = float(request.GET.get("simplify", "0.001"))
    except (TypeError, ValueError):
        tolerance = 0.001

    # Constrain tolerance to safe range to prevent DoS or performance degradation
    tolerance = max(0.0001, min(tolerance, 0.01))

    # Query SQL diretta con PostGIS per semplificazione veloce
    # Include media radon e area prioritaria tramite LEFT JOIN
    sql = """
        SELECT
            m."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist" as codice_istat,
            m."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_nom" as nome,
            m."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.provin_nom" as provincia,
            m."esri_geodatabase.geoportale.rad_18_tab_comuni_radon.media" as media_radon,
            a."esri_geodatabase.geoportale.rad_18_tab_comuni_radon.ap" as area_prioritaria,
            ST_AsGeoJSON(ST_Simplify(m.geom, %s), 5) as geom_json
        FROM medie_radon_comunali m
        LEFT JOIN aree_prioritarie_radon a
            ON m."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist" =
               a."esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist"
        WHERE m.geom IS NOT NULL
          AND ST_IsValid(m.geom) = true
          AND ST_GeometryType(m.geom) IN ('ST_Polygon', 'ST_MultiPolygon')
        ORDER BY nome
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [tolerance])
            rows = cursor.fetchall()
    except DatabaseError as e:
        logger.error(f"Database error fetching comuni GeoJSON: {e}")
        return JsonResponse({"error": "Failed to fetch geographic data"}, status=500)

    features = []
    for row in rows:
        try:
            codice_istat, nome, provincia, media_radon, area_prioritaria, geom_json = row

            # Skip if geometry is NULL (should not happen due to WHERE clause)
            if not geom_json:
                logger.warning(f"Null geometry for comune {nome}")
                continue

            # Parse GeoJSON geometry
            try:
                geometry = json.loads(geom_json)
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Invalid geometry JSON for comune {nome}: {e}")
                continue

            # Format media radon for cleaner display
            media_radon_formatted = round(media_radon, 1) if media_radon is not None else None

            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "codice_istat": codice_istat,
                        "nome": nome,
                        "provincia": provincia,
                        "media_radon": media_radon_formatted,
                        "area_prioritaria": area_prioritaria or "N/D",
                    },
                    "geometry": geometry,
                }
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Error processing row data: {e}")
            continue

    return JsonResponse({"type": "FeatureCollection", "features": features})
