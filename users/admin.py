# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from .models import CustomUser  # Assicurati che il modello si chiami CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UnfoldModelAdmin, UserAdmin):
    # UserAdmin gestisce già password hashata, gruppi, permessi, ecc.
    # Se hai campi custom (es. 'telefono'), dovrai aggiungerli ai fieldsets qui sotto.
    # Hereditiamo i fieldsets predefiniti da UserAdmin e li espandiamo (se necessario)
    fieldsets = UserAdmin.fieldsets

    # Definisci i campi che appaiono nella lista (list_display)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "gender",
        "is_staff",
    )

    # Aggiungi eventuali campi custom che hai su CustomUser in un nuovo fieldset qui sotto
    # fieldsets = UserAdmin.fieldsets + ( (None, {'fields': ('il_tuo_campo_custom',)}), )

    # Il resto della logica UserAdmin è ereditata...
