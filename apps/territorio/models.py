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

    # 4. CONCENTRAZIONE MEDIA RADON
    media_radon = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Concentrazione Media Radon (Bq/m³)",
        db_column="esri_geodatabase.geoportale.rad_18_tab_comuni_radon.media",
    )

    # 5. GEOMETRIA
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


class AreaPrioritariaRadon(models.Model):
    """Modello per le aree prioritarie secondo il Piano Radon."""

    codice_istat = models.CharField(
        primary_key=True,
        max_length=50,
        verbose_name="Codice ISTAT",
        db_column="esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_ist",
    )

    nome = models.CharField(
        max_length=255,
        verbose_name="Comune",
        db_column="esri_geodatabase.geoportale.lim_01_comuni_in_vigore.comune_nom",
    )

    provincia = models.CharField(
        max_length=255,
        verbose_name="Provincia",
        db_column="esri_geodatabase.geoportale.lim_01_comuni_in_vigore.provin_nom",
    )

    area_prioritaria = models.CharField(
        max_length=10,
        verbose_name="Area Prioritaria",
        db_column="esri_geodatabase.geoportale.rad_18_tab_comuni_radon.ap",
        help_text="Indica se il comune è in area prioritaria secondo il Piano Radon",
    )

    geom = models.PolygonField(
        srid=4326,
        verbose_name="Confini Amministrativi",
        db_column="geom",
    )

    class Meta:
        managed = False
        db_table = "aree_prioritarie_radon"
        verbose_name = "Area Prioritaria Radon"
        verbose_name_plural = "Aree Prioritarie Radon"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} - AP: {self.area_prioritaria}"


class ComuneCompleto(models.Model):
    """
    VIEW che unisce tutti i dati disponibili per ogni comune:
    - Dati base e media radon
    - Area prioritaria
    - Informazioni geologiche
    - Permeabilità
    - Distanza da faglie
    """

    codice_istat = models.CharField(
        primary_key=True,
        max_length=50,
        verbose_name="Codice ISTAT",
    )

    nome = models.CharField(
        max_length=255,
        verbose_name="Comune",
    )

    provincia = models.CharField(
        max_length=255,
        verbose_name="Provincia",
    )

    media_radon = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Concentrazione Media Radon (Bq/m³)",
    )

    area_prioritaria = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Area Prioritaria Piano Radon",
    )

    # Dati geologici
    unita_litologica = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Unità Litologica",
    )

    litologia = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Litologia",
    )

    eta_geologica = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name="Età Geologica",
    )

    descrizione_geologica = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Descrizione Geologica",
    )

    dominio_geologico = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Dominio Geologico",
    )

    # Permeabilità
    classe_permeabilita = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Classe Permeabilità",
        help_text="1=Alta, 2=Media, 3=Bassa, 4=Molto Bassa",
    )

    # Faglie
    distanza_faglia_m = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Distanza dalla Faglia più vicina (m)",
    )

    tipo_faglia_vicina = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Tipo Faglia più vicina",
    )

    geom = models.PolygonField(
        srid=4326,
        verbose_name="Confini Amministrativi",
    )

    class Meta:
        managed = False
        db_table = "comuni_completi"
        verbose_name = "Comune Completo"
        verbose_name_plural = "Comuni Completi"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.provincia})"
