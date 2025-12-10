from concurrency.fields import IntegerVersionField
from django.db import models


class TraceableModel(models.Model):
    """
    Modello astratto che fornisce tracciamento automatico di creazione,
    aggiornamento e gestione della concorrenza ottimistica.

    Tutti i modelli del progetto dovrebbero ereditare da questa classe per
    beneficiare di funzionalità comuni di auditing e controllo delle versioni.

    Utilizzo:
        Per abilitare anche il tracciamento della cronologia (history tracking),
        i modelli concreti devono includere esplicitamente HistoricalRecords:

        Example:
            ```python
            from django.db import models
            from simple_history.models import HistoricalRecords
            from apps.core.models import TraceableModel

            class MioModello(TraceableModel):
                nome = models.CharField(max_length=100)
                # Abilita history tracking ereditando i campi da TraceableModel
                history = HistoricalRecords(inherit=True)

                class Meta:
                    verbose_name = "Mio Modello"
            ```

    Attributi:
        created_at: Timestamp di creazione (auto-popolato, non modificabile)
        updated_at: Timestamp dell'ultimo aggiornamento (auto-aggiornato)
        version: Campo per il controllo di concorrenza ottimistico (django-concurrency)

    Note:
        - created_at e updated_at sono gestiti automaticamente da Django
        - version previene modifiche concorrenti usando optimistic locking
        - L'ordering predefinito è per created_at discendente (più recenti prima)
    """

    # Timestamp fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        db_index=True,
        help_text="Data e ora di creazione",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        db_index=True,
        help_text="Data e ora dell'ultimo aggiornamento",
    )

    # Concurrency control - automatic optimistic locking
    version = IntegerVersionField(
        help_text="Versione del record per il controllo automatico della concorrenza",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]
