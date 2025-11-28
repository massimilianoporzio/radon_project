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
from django.urls import reverse_lazy  # noqa: E402, I001
# --- APPLICAZIONI ---

# --- DJANGO UNFOLD CONFIGURATION ---

UNFOLD = {
    # --- 1. BRANDING E TITOLI ---
    "SITE_TITLE": "Monitoraggio Radon ASL",
    "SITE_HEADER": "Sistema GIS Radon",
    "SITE_SYMBOL": "public",
    "STYLES": [
        "css/custom_admin.css",  # Esempio: non serve la lambda, basta la stringa
    ],
    # --- 2. CONFIGURAZIONE SIDEBAR ---
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,  # Mostra solo i gruppi definiti qui
        "navigation": [
            # GRUPPO 1: DATI CORE GIS/AMMINISTRATIVI
            {
                "title": "Dati Geografici & Amministrativi",
                "separator": True,
                "items": [
                    {
                        "title": "Comuni ARPA",
                        "icon": "globe",
                        "link": reverse_lazy("admin:territorio_comunearpa_changelist"),
                        # Chiunque abbia il permesso di vedere i Comuni ARPA
                        "permission": lambda request: request.user.has_perm("territorio.view_comunearpa"),
                    },
                    # Futuro: Edifici e Piani (useranno permessi custom)
                ],
            },
            # GRUPPO 2: ACCESSO E SICUREZZA
            {
                "title": "Accesso & Utenti",
                "separator": True,
                "items": [
                    # ✔️ Utenti Custom (Visibile agli staff/superusers)
                    {
                        "title": "Utenti",
                        "icon": "person",
                        "link": reverse_lazy("admin:users_customuser_changelist"),
                        "permission": lambda request: request.user.is_staff,
                    },
                    # ✔️ Gruppi e Permessi (SOLO Superuser)
                    {
                        "title": "Gruppi & Permessi",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    # ✔️ Honeypot (SOLO Superuser per la sicurezza)
                    {
                        "title": "Log Tentativi",
                        "icon": "shield",
                        "link": reverse_lazy("admin:admin_honeypot_loginattempt_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
            # GRUPPO 3: ARCHITETTURA E LOG (Manutenzione del Sistema)
            {
                "title": "Gestione Tecnica & Log",
                "separator": True,
                "items": [
                    {
                        "title": "Cronologia Modifiche",
                        "icon": "history",
                        # FIX: Punti all'indice Admin finché non c'è il primo modello tracciato
                        "link": reverse_lazy("admin:index"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
        ],
    },
    # --- 3. ALTRE IMPOSTAZIONI (Opzionali) ---
    "COLORS": {
        "base": {
            "50": "oklch(98.5% .002 247.839)",
            "100": "oklch(96.7% .003 264.542)",
            "200": "oklch(92.8% .006 264.531)",
            "300": "oklch(87.2% .01 258.338)",
            "400": "oklch(70.7% .022 261.325)",
            "500": "oklch(55.1% .027 264.364)",
            "600": "oklch(44.6% .03 256.802)",
            "700": "oklch(37.3% .034 259.733)",
            "800": "oklch(27.8% .033 256.848)",
            "900": "oklch(21% .034 264.665)",
            "950": "oklch(13% .028 261.692)",
        },
        "primary": {
            # Cambia l'ultimo valore (il Tono) da 308/307 a 170 circa.
            "50": "#e7fff8",  # Era 308.299
            "100": "#c6ffec",  # Era 307.174
            "200": "#92ffdf",  # Era 306.703
            "300": "#4dffd2",  # Era 306.383
            "400": "#0fffc3",  # Era 305.504
            "500": "#00e8ac",  # Era 303.9 - Questo è il colore principale!
            "600": "#00be8e",  # Era 302.321
            "700": "#009876",  # Era 301.924
            "800": "#00785f",  # Era 303.724
            "900": "#00624f",  # Era 304.987
            "950": "#00382e",  # Era 302.717
        },
    },
}
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
    "simple_history",
    "concurrency",
    "drf_yasg",
]

LOCAL_APPS = [
    "users",
    "territorio",
]

# La concatenazione finale è corretta:
INSTALLED_APPS = UI_APPS + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


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
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
