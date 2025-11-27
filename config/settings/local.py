import logging  # <--- 1. Aggiungi questo import
import os
import sys
from pathlib import Path

from .base import *  # noqa

# <--- 2. Inizializza il logger
logger = logging.getLogger(__name__)
# --- SVILUPPO ---
DEBUG = True

# In sviluppo accettiamo tutto per comodità
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "[::1]",
]

# --- LOGGING SU CONSOLE ---
# Vediamo tutto colorato nel terminale
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "colored"},
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
        # Scommenta sotto se vuoi vedere le query SQL nel terminale
        # 'django.db.backends': {'handlers': ['console'], 'level': 'DEBUG'},
    },
}

# ==========================================
# FIX CRITICO PER GDAL SU WINDOWS (UV/PIP)
# ==========================================
if os.name == "nt":
    # 1. Calcoliamo il percorso della cartella 'osgeo' nel venv
    # Struttura tipica: .venv/Lib/site-packages/osgeo
    VENV_ROOT = Path(sys.prefix)
    OSGEO_ROOT = VENV_ROOT / "Lib" / "site-packages" / "osgeo"

    if OSGEO_ROOT.exists():
        # Aggiungiamo osgeo al PATH di sistema (fondamentale per caricare le dipendenze)
        os.environ["PATH"] = str(OSGEO_ROOT) + ";" + os.environ["PATH"]

        # 2. Configura GDAL
        # Cerchiamo la DLL principale (es. gdal304.dll) escludendo file accessori
        gdal_dlls = [
            f for f in OSGEO_ROOT.glob("gdal*.dll") if not f.name.endswith("const.dll") and not f.name.endswith("_i.dll")
        ]

        if gdal_dlls:
            # Prende il primo file gdalXXX.dll valido
            GDAL_LIBRARY_PATH = str(gdal_dlls[0])

        # 3. Configura GEOS (CRITICO: Deve essere geos_c.dll)
        # Django richiede l'interfaccia C, non la libreria C++ (geos.dll)
        geos_c_dll = OSGEO_ROOT / "geos_c.dll"

        if geos_c_dll.exists():
            GEOS_LIBRARY_PATH = str(geos_c_dll)
        else:
            # Fallback (ma rischioso) se non trova geos_c.dll
            geos_dlls = list(OSGEO_ROOT.glob("geos*.dll"))
            if geos_dlls:
                GEOS_LIBRARY_PATH = str(geos_dlls[0])

    else:
        logger.warning("ATTENZIONE: Cartella osgeo non trovata in %s. Hai installato il wheel GDAL?", OSGEO_ROOT)
