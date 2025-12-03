import json

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import JsonResponse


@login_required
def comuni_geojson(request):
    """
    API endpoint che restituisce TUTTI i comuni in formato GeoJSON semplificato.
    Il filtro per provincia viene gestito client-side per evitare ricaricamenti.
    La semplificazione avviene a livello database con PostGIS per performance ottimali.
    """
    tolerance = float(request.GET.get("simplify", "0.001"))

    # Query SQL diretta con PostGIS per semplificazione veloce
    # Usa i nomi delle colonne dal modello e filtra solo comuni con geometria valida
    sql = """
        SELECT
            "esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist" as codice_istat,
            "esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_nom" as nome,
            "esri_geodatabase.geoportale.lim_01_comuni_in_vigore.provin_nom" as provincia,
            ST_AsGeoJSON(ST_Simplify(geom, %s), 5) as geom_json
        FROM medie_radon_comunali
        WHERE geom IS NOT NULL
          AND ST_IsValid(geom) = true
          AND ST_GeometryType(geom) IN ('ST_Polygon', 'ST_MultiPolygon')
        ORDER BY nome
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, [tolerance])
        rows = cursor.fetchall()

    features = []
    for row in rows:
        codice_istat, nome, provincia, geom_json = row

        # Salta se la geometria è ancora NULL (non dovrebbe succedere con il WHERE)
        if not geom_json:
            continue

        features.append(
            {
                "type": "Feature",
                "properties": {
                    "codice_istat": codice_istat,
                    "nome": nome,
                    "provincia": provincia,
                },
                "geometry": json.loads(geom_json),
            }
        )

    return JsonResponse({"type": "FeatureCollection", "features": features})
