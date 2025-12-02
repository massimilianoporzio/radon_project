from django.templatetags.static import static
from django.urls import reverse_lazy

UNFOLD = {
    # --- 1. BRANDING E TITOLI ---
    "SITE_TITLE": "Monitoraggio Radon ASL",
    "SITE_HEADER": "Sistema GIS Radon",
    "SITE_SYMBOL": "public",
    "STYLES": [
        lambda request: static("css/custom_admin.css"),
    ],
    "SCRIPTS": [
        lambda request: static("js/admin_custom.js"),
    ],
    # --- 2. CONFIGURAZIONE SIDEBAR ---
    "SIDEBAR": {
        "show_search": False,
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
                        "title": "Tentativi di Login",
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
            "50": "oklch(98.2% 0.04 170)",
            "100": "oklch(95.4% 0.08 170)",
            "200": "oklch(90.5% 0.14 170)",
            "300": "oklch(85.1% 0.19 170)",
            "400": "oklch(81.5% 0.23 170)",
            "500": "oklch(79.1% 0.21 170)",  # Colore principale
            "600": "oklch(65.8% 0.16 170)",
            "700": "oklch(55.2% 0.13 170)",
            "800": "oklch(46.1% 0.10 170)",
            "900": "oklch(39.8% 0.08 170)",
            "950": "oklch(25.0% 0.05 170)",
        },
    },
    # CONFIGURAZIONE LOGIN
    "LOGIN": {
        # Questa è l'immagine che vedi nella demo.
        # Puoi mettere un link esterno o un file statico locale.
        "image": lambda request: static("images/login-bg.jpg"),
        # Opzionale: reindirizzamento dopo il login
        "redirect_after": "admin:index",
    },
}
