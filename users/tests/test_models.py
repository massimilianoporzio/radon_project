import pytest
from django.contrib.auth import get_user_model

# Recuperiamo il modello utente attivo (il tuo CustomUser)
User = get_user_model()


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

    with pytest.raises(Exception):  # Django lancerà un errore di integrità
        User.objects.create_user(username="user2", email="unique@test.com", password="pwd")
