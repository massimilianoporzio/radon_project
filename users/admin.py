# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User  # Assicurati che il modello si chiami User

# Registriamo il tuo User custom usando la logica standard di Django
# (così vedi i campi password, permessi, gruppi, ecc. formattati bene)
admin.site.register(User, UserAdmin)
