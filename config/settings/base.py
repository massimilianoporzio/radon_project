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

# --- APPLICAZIONI ---
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",  # GeoDjango (PostGIS)
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "admin_honeypot",
]

LOCAL_APPS = [
    "users",  # La tua app utenti (CustomUser)
    # 'core',  # Scommenta quando creeremo l'app core
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
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
LANGUAGE_CODE = "it-it"
TIME_ZONE = "Europe/Rome"
USE_I18N = True
USE_TZ = True

# --- STATIC FILES ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
