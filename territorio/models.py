from django.contrib.gis.db import models


class ComuneArpa(models.Model):
    # 1. CODICE ISTAT (Chiave Primaria)
    # Nel bozza dovrebbe essere qualcosa tipo '...comune_ist'
    codice_istat = models.CharField(
        primary_key=True,
        max_length=50,
        verbose_name="Codice ISTAT",
        # VERIFICA CHE QUESTA STRINGA SIA ESATTA nel tuo file bozza:
        db_column="esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist",
    )

    # 2. NOME COMUNE
    # Nel bozza dovrebbe essere '...comune_nom'
    nome = models.CharField(
        max_length=255,
        verbose_name="Comune",
        # VERIFICA QUESTA STRINGA:
        db_column="esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_nom",
    )

    # 3. PROVINCIA
    # Nel bozza dovrebbe essere '...provin_nom'
    provincia = models.CharField(
        max_length=255,
        verbose_name="Provincia",
        # VERIFICA QUESTA STRINGA:
        db_column="esri_geodatabase.geoportale.lim_01_comuni_in_vigore.provin_nom",
    )

    # 4. GEOMETRIA
    # Cerca la riga 'geom =' o 'wkb_geometry =' nel bozza.
    # Controlla anche il numero SRID (spesso è 32632 o 3003 per dati italiani).
    geom = models.PolygonField(
        srid=4326,  # <--- CAMBIA QUESTO NUMERO se nel bozza vedi un numero diverso!
        verbose_name="Confini Amministrativi",
        db_column="geom",  # Se nel bozza si chiama 'wkb_geometry', scrivi quello qui.
    )

    class Meta:
        managed = False  # CRUCIALE: Django legge solo, non modifica.
        db_table = "medie_radon_comunali"
        verbose_name = "Comune ARPA"
        verbose_name_plural = "Comuni ARPA"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.provincia})"
