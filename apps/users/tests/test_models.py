import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import SimpleTestCase

from apps.users.models import CustomUser

# Recuperiamo il modello utente attivo (il tuo CustomUser)
User = get_user_model()


class CustomUserModelTest(SimpleTestCase):
    """Test CustomUser model methods without DB"""

    def test_str_representation_full(self):
        """Test __str__ with full name"""
        user = CustomUser(
            username="testuser",
            first_name="Mario",
            last_name="Rossi",
        )
        expected = "Mario Rossi (testuser)"
        self.assertEqual(str(user), expected)

    def test_str_representation_partial(self):
        """Test __str__ with only username"""
        user = CustomUser(
            username="testuser",
            first_name="",
            last_name="",
        )
        expected = "  (testuser)"
        self.assertEqual(str(user), expected)

    def test_str_representation_with_first_name_only(self):
        """Test __str__ with only first name"""
        user = CustomUser(
            username="testuser",
            first_name="Mario",
            last_name="",
        )
        expected = "Mario  (testuser)"
        self.assertEqual(str(user), expected)

    def test_gender_choices(self):
        """Test gender field has correct choices"""
        self.assertEqual(CustomUser.MALE, "M")
        self.assertEqual(CustomUser.FEMALE, "F")
        self.assertEqual(CustomUser.GENDER_CHOICES[0], ("M", "Maschio"))
        self.assertEqual(CustomUser.GENDER_CHOICES[1], ("F", "Femmina"))

    def test_default_gender_is_male(self):
        """Test default gender is MALE"""
        # Check field default (not saved to DB)
        field = CustomUser._meta.get_field("gender")
        self.assertEqual(field.default, CustomUser.MALE)

    def test_email_field_unique(self):
        """Test email field has unique=True constraint"""
        field = CustomUser._meta.get_field("email")
        self.assertTrue(field.unique)


@pytest.mark.django_db
def test_create_user():
    """Verifica che si possa creare un utente normale con email."""
    user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.check_password("password123")
    assert user.is_active


@pytest.mark.django_db
def test_create_superuser():
    """Verifica che il superuser abbia i permessi corretti."""
    admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="password123")
    assert admin.is_superuser
    assert admin.is_staff
    assert admin.is_active


@pytest.mark.django_db
def test_email_unique():
    """Verifica che non si possano creare due utenti con la stessa email."""
    User.objects.create_user(username="user1", email="unique@test.com", password="pwd")

    with pytest.raises(IntegrityError):  # Django lancerà un errore di integrità
        User.objects.create_user(username="user2", email="unique@test.com", password="pwd")
