import os
from pathlib import Path

import environ

# --- PERCORSI ---
# Risaliamo di 3 livelli: config/settings/base.py -> config/settings -> config -> ROOT
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- GESTIONE VARIABILI D'AMBIENTE ---
env = environ.Env()
# Legge il file .env nella root del progetto (se esiste)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

DEBUG = env.bool("DJANGO_DEBUG", False)

# --- SICUREZZA ---
if DEBUG:
    # In SVILUPPO (Locale):
    # Se manca la chiave nel .env, ne usiamo una finta per comodità.
    SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-dev-key-do-not-use-in-prod")
else:
    # In PRODUZIONE (Online):
    # NON mettiamo nessun default.
    # Se la variabile manca nel file .env o nelle config del server,
    # django-environ solleverà un errore "ImproperlyConfigured" e il server non partirà.
    # Questo ti salva da disastri di sicurezza.
    SECRET_KEY = env("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = []
# --- UI CONFIG (Import from dedicated file) ---
from .unfold_config import UNFOLD  # <--- NUOVO IMPORT!  # noqa: E402, F401, I001

# --- APPLICAZIONI ---

# --- DJANGO UNFOLD CONFIGURATION ---
# La configurazione UNFOLD è centralizzata in `config/settings/unfold_config.py`.
# 1. UI APPS (Ordine Garantito)
UI_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.location_field",
    "unfold.contrib.simple_history",
]

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "admin_honeypot",
    # ⚠️ TORNIAMO AL NOME COMPLETO PERCHÉ È NECESSARIO
    "location_field.apps.DefaultConfig",
    "leaflet",
    "simple_history",
    "drf_yasg",
]

LOCAL_APPS = [
    "apps.core",
    "apps.users",
    "apps.territorio",
]

# La concatenazione finale è corretta:
INSTALLED_APPS = UI_APPS + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "crum.CurrentRequestUserMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- DATABASE (PostGIS) ---
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}

# --- CUSTOM USER MODEL ---
AUTH_USER_MODEL = "users.CustomUser"

# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = "it"
TIME_ZONE = "Europe/Rome"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Diciamo a Django dove salvare le traduzioni
LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

# --- STATIC FILES ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- LEAFLET CONFIGURATION ---
LEAFLET_CONFIG = {
    "DEFAULT_CENTER": (45.0, 7.6),  # Centro sul Piemonte
    "DEFAULT_ZOOM": 8,
    "MIN_ZOOM": 7,
    "MAX_ZOOM": 18,
    "SCALE": "both",
    "ATTRIBUTION_PREFIX": "Powered by django-leaflet",
    "TILES": [
        (
            "OpenStreetMap",
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                "attribution": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                "maxZoom": 19,
            },
        ),
    ],
    "SPATIAL_EXTENT": (6.0, 43.5, 9.5, 46.5),  # Confini Piemonte approssimativi
    "PLUGINS": {
        "forms": {
            "auto-include": True,
        },
    },
}
