import os

from .base import *  # noqa

DEBUG = False

# Metti qui l'IP del server Windows o il dominio intranet
ALLOWED_HOSTS = ["192.168.1.100", "localhost", "127.0.0.1"]

# Sicurezza base
X_FRAME_OPTIONS = "DENY"

# Log su file per Waitress/Windows
LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "django_error.log"),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

USE_HTTPS = env.bool("DJANGO_USE_HTTPS", default=False)

if USE_HTTPS:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS: Attenzione! Questo dice al browser "Ricordati di usare SOLO HTTPS per 1 anno".
    # In intranet è pericoloso: se scade il certificato, nessuno accede più al sito.
    # Ti consiglio di tenerlo basso o spento all'inizio.
    SECURE_HSTS_SECONDS = 60  # Inizia con 60 secondi per testare, poi aumenta
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
else:
    # Se siamo in HTTP (es. intranet vecchia), questi devono stare spenti
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
