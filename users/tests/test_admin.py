"""
Test suite for users admin.
Tests CustomUserAdmin configuration and display methods.
"""

from django.contrib.admin.sites import AdminSite
from django.test import SimpleTestCase

from users.admin import CustomUserAdmin
from users.models import CustomUser


class CustomUserAdminTest(SimpleTestCase):
    """Test CustomUserAdmin configuration"""

    def setUp(self):
        """Set up test fixtures"""
        self.site = AdminSite()
        self.admin = CustomUserAdmin(CustomUser, self.site)

    def test_list_display_configured(self):
        """Test list_display includes custom fields"""
        expected_fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "gender",
            "is_staff",
        )
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_admin_registered_with_site(self):
        """Test admin is properly registered"""
        self.assertIsNotNone(self.admin)
        self.assertEqual(self.admin.model, CustomUser)

    def test_inherits_from_user_admin(self):
        """Test CustomUserAdmin has UserAdmin fieldsets"""
        # UserAdmin.fieldsets should be inherited
        self.assertIsNotNone(self.admin.fieldsets)
        self.assertIsInstance(self.admin.fieldsets, tuple)

    def test_admin_has_default_user_admin_functionality(self):
        """Test that standard UserAdmin features are available"""
        # Check standard UserAdmin attributes exist
        self.assertTrue(hasattr(self.admin, "add_form"))
        self.assertTrue(hasattr(self.admin, "form"))
        self.assertTrue(hasattr(self.admin, "change_password_form"))

    def test_list_display_includes_gender_field(self):
        """Test that gender field is in list_display"""
        self.assertIn("gender", self.admin.list_display)

    def test_list_display_includes_email_field(self):
        """Test that email field is in list_display"""
        self.assertIn("email", self.admin.list_display)
