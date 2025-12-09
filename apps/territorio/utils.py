"""
Utility functions for territorio app.
Shared logic to avoid code duplication.
"""

import environ

# Leggi variabili d'ambiente
env = environ.Env()

# Soglie radon (Bq/m³) - Fonte unica di verità
# Configurabili tramite .env, con fallback ai valori standard
RADON_THRESHOLD_HIGH = env.int("RADON_THRESHOLD_HIGH", default=300)  # Rosso: rischio alto
RADON_THRESHOLD_MEDIUM = env.int("RADON_THRESHOLD_MEDIUM", default=200)  # Arancione: rischio medio
# < RADON_THRESHOLD_MEDIUM = Verde: rischio basso


def get_area_prioritaria_badge_class(area_prioritaria: str | None) -> str:
    """
    Restituisce la classe CSS Tailwind per il badge area prioritaria.

    Args:
        area_prioritaria: Stringa con l'area prioritaria ("prioritaria", "attenzionata", etc.)

    Returns:
        Classe CSS per il badge (es. "bg-red-600 text-white")
    """
    # Default: grigio
    badge_class = "bg-gray-500 text-white dark:bg-gray-600"

    if not area_prioritaria:
        return badge_class

    ap_lower = area_prioritaria.lower()

    # Prioritaria (rosso) - ma NON "non prioritaria"
    if "prioritari" in ap_lower and "non" not in ap_lower:
        badge_class = "bg-red-600 text-white"
    # Attenzionata (arancione)
    elif "attenzione" in ap_lower:
        badge_class = "bg-amber-500 text-white"
    # Non prioritaria (verde)
    elif "non prioritari" in ap_lower:
        badge_class = "bg-emerald-600 text-white"

    return badge_class
