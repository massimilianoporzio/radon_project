from django.db import models
from simple_history.models import HistoricalRecords


class TraceableModel(models.Model):
    """
    Modello astratto che fornisce tracciamento automatico di creazione,
    aggiornamento, cronologia e gestione della concorrenza.

    Tutti i modelli del progetto dovrebbero ereditare da questa classe.
    """

    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data e ora di creazione")
    updated_at = models.DateTimeField(auto_now=True, help_text="Data e ora dell'ultimo aggiornamento")

    # Concurrency control (IntegerField per tracciare le versioni)
    version = models.IntegerField(default=0, help_text="Versione del record per il controllo della concorrenza")

    # History tracking
    history = HistoricalRecords()

    class Meta:
        abstract = True
        ordering = ["-created_at"]
