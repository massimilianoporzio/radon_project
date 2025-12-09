from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    pass


class CustomUser(AbstractUser):
    MALE = "M"
    FEMALE = "F"
    GENDER_CHOICES = (
        (MALE, "Maschio"),
        (FEMALE, "Femmina"),
    )

    # Nota: AbstractUser ha già first_name, last_name, email.
    # Li sovrascriviamo solo se vuoi cambiare opzioni (es. email unique=True che è ottima cosa).

    gender = models.CharField(max_length=1, blank=True, choices=GENDER_CHOICES, default=MALE)

    # Rendiamo l'email obbligatoria e unica (best practice moderna)
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
