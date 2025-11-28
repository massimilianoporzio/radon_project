# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from .models import CustomUser  # Assicurati che il modello si chiami CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin, UnfoldModelAdmin):
    # UserAdmin gestisce già password hashata, gruppi, permessi, ecc.
    # Se hai campi custom (es. 'telefono'), dovrai aggiungerli ai fieldsets qui sotto.
    pass
