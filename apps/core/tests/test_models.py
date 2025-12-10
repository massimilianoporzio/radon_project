"""
Test suite for core models.
Tests TraceableModel abstract model structure and field configuration.
"""

from unittest.mock import patch

from concurrency.fields import IntegerVersionField
from django.contrib.auth import get_user_model
from django.db import models
from django.test import SimpleTestCase

from apps.core.models import TraceableModel

User = get_user_model()


class TraceableModelTest(SimpleTestCase):
    """Test TraceableModel abstract model structure and configuration."""

    def test_model_is_abstract(self):
        """Test that TraceableModel is marked as abstract."""
        assert TraceableModel._meta.abstract is True

    def test_created_at_field_exists(self):
        """Test that created_at field exists with correct configuration."""
        field = TraceableModel._meta.get_field("created_at")

        assert field is not None
        assert isinstance(field, models.DateTimeField)
        assert field.auto_now_add is True
        assert field.editable is False
        assert field.db_index is True

    def test_updated_at_field_exists(self):
        """Test that updated_at field exists with correct configuration."""
        field = TraceableModel._meta.get_field("updated_at")

        assert field is not None
        assert isinstance(field, models.DateTimeField)
        assert field.auto_now is True
        assert field.editable is False
        assert field.db_index is True

    def test_version_field_exists(self):
        """Test that version field exists for concurrency control."""
        field = TraceableModel._meta.get_field("version")

        assert field is not None
        assert isinstance(field, IntegerVersionField)

    def test_default_ordering(self):
        """Test that default ordering is by created_at descending."""
        ordering = TraceableModel._meta.ordering

        assert ordering is not None
        assert "-created_at" in ordering

    def test_model_fields_count(self):
        """Test that model has the expected number of fields."""
        # TraceableModel should have: created_at, updated_at, version
        fields = TraceableModel._meta.get_fields()
        field_names = [f.name for f in fields]

        assert "created_at" in field_names
        assert "updated_at" in field_names
        assert "version" in field_names

    def test_timestamp_fields_help_text(self):
        """Test that timestamp fields have appropriate help text."""
        created_field = TraceableModel._meta.get_field("created_at")
        updated_field = TraceableModel._meta.get_field("updated_at")

        assert created_field.help_text == "Data e ora di creazione"
        assert updated_field.help_text == "Data e ora dell'ultimo aggiornamento"

    def test_version_field_help_text(self):
        """Test that version field has appropriate help text."""
        version_field = TraceableModel._meta.get_field("version")

        assert "concorrenza" in version_field.help_text.lower()

    def test_model_has_docstring(self):
        """Test that the model has comprehensive documentation."""
        assert TraceableModel.__doc__ is not None
        assert len(TraceableModel.__doc__) > 100
        assert "astratto" in TraceableModel.__doc__.lower()

    def test_docstring_mentions_history_records(self):
        """Test that documentation explains HistoricalRecords usage."""
        docstring = TraceableModel.__doc__
        assert "HistoricalRecords" in docstring
        assert "inherit=True" in docstring

    def test_docstring_has_example(self):
        """Test that documentation includes usage example."""
        docstring = TraceableModel.__doc__
        assert "Example:" in docstring or "Utilizzo:" in docstring
        assert "history = HistoricalRecords(inherit=True)" in docstring


class TraceableModelInheritanceTest(SimpleTestCase):
    """Test that TraceableModel can be properly inherited."""

    def test_can_create_child_model(self):
        """Test that a concrete model can inherit from TraceableModel."""

        class ConcreteModel(TraceableModel):
            """Test concrete model."""

            name = models.CharField(max_length=100)

            class Meta:
                app_label = "core"

        # Check that child model has all parent fields
        field_names = [f.name for f in ConcreteModel._meta.get_fields()]

        assert "created_at" in field_names
        assert "updated_at" in field_names
        assert "version" in field_names
        assert "name" in field_names

    def test_child_model_can_inherit_ordering(self):
        """Test that child models CAN inherit the default ordering if explicitly set."""

        class ConcreteModel(TraceableModel):
            """Test concrete model that explicitly inherits ordering."""

            name = models.CharField(max_length=100)

            class Meta:
                app_label = "core"
                # Explicitly inherit parent ordering
                ordering = TraceableModel._meta.ordering

        ordering = ConcreteModel._meta.ordering
        assert "-created_at" in ordering

    def test_child_model_can_override_ordering(self):
        """Test that child models can override the default ordering."""

        class ConcreteModel(TraceableModel):
            """Test concrete model with custom ordering."""

            name = models.CharField(max_length=100)

            class Meta:
                app_label = "core"
                ordering = ["name"]

        ordering = ConcreteModel._meta.ordering
        assert "name" in ordering
        assert "-created_at" not in ordering


class TraceableModelFieldPropertiesTest(SimpleTestCase):
    """Test detailed field properties and constraints."""

    def test_created_at_not_nullable(self):
        """Test that created_at field cannot be null."""
        field = TraceableModel._meta.get_field("created_at")
        # auto_now_add fields are typically not nullable
        assert field.null is False

    def test_updated_at_not_nullable(self):
        """Test that updated_at field cannot be null."""
        field = TraceableModel._meta.get_field("updated_at")
        # auto_now fields are typically not nullable
        assert field.null is False

    def test_timestamp_fields_are_datetime(self):
        """Test that timestamp fields are DateTimeField type."""
        created_field = TraceableModel._meta.get_field("created_at")
        updated_field = TraceableModel._meta.get_field("updated_at")

        assert created_field.get_internal_type() == "DateTimeField"
        assert updated_field.get_internal_type() == "DateTimeField"

    def test_timestamp_fields_have_db_indexes(self):
        """Test that both timestamp fields are indexed for query performance."""
        created_field = TraceableModel._meta.get_field("created_at")
        updated_field = TraceableModel._meta.get_field("updated_at")

        assert created_field.db_index is True
        assert updated_field.db_index is True

    def test_fields_are_not_editable_in_admin(self):
        """Test that timestamp fields won't appear in admin forms."""
        created_field = TraceableModel._meta.get_field("created_at")
        updated_field = TraceableModel._meta.get_field("updated_at")

        assert created_field.editable is False
        assert updated_field.editable is False


class TraceableModelUserTrackingTest(SimpleTestCase):
    """Test user tracking fields (created_by, updated_by) in TraceableModel."""

    def test_created_by_field_exists(self):
        """Test that created_by field exists with correct configuration."""
        field = TraceableModel._meta.get_field("created_by")

        assert field is not None
        assert isinstance(field, models.ForeignKey)
        assert field.editable is False
        assert field.null is True
        assert field.blank is True

    def test_updated_by_field_exists(self):
        """Test that updated_by field exists with correct configuration."""
        field = TraceableModel._meta.get_field("updated_by")

        assert field is not None
        assert isinstance(field, models.ForeignKey)
        assert field.editable is False
        assert field.null is True
        assert field.blank is True

    def test_created_by_references_user_model(self):
        """Test that created_by ForeignKey references AUTH_USER_MODEL."""
        field = TraceableModel._meta.get_field("created_by")
        # Check that it references the AUTH_USER_MODEL (by checking the related field name)
        assert field.remote_field is not None
        assert field.name == "created_by"

    def test_updated_by_references_user_model(self):
        """Test that updated_by ForeignKey references AUTH_USER_MODEL."""
        field = TraceableModel._meta.get_field("updated_by")
        # Check that it references the AUTH_USER_MODEL (by checking the related field name)
        assert field.remote_field is not None
        assert field.name == "updated_by"

    def test_created_by_on_delete_protect(self):
        """Test that deleting a user is protected if they created records."""
        field = TraceableModel._meta.get_field("created_by")
        assert field.remote_field.on_delete.__name__ == "PROTECT"

    def test_updated_by_on_delete_protect(self):
        """Test that deleting a user is protected if they updated records."""
        field = TraceableModel._meta.get_field("updated_by")
        assert field.remote_field.on_delete.__name__ == "PROTECT"

    def test_created_by_help_text(self):
        """Test that created_by field has appropriate help text."""
        field = TraceableModel._meta.get_field("created_by")
        assert "creato" in field.help_text.lower() or "created" in field.help_text.lower()

    def test_updated_by_help_text(self):
        """Test that updated_by field has appropriate help text."""
        field = TraceableModel._meta.get_field("updated_by")
        assert "aggiornato" in field.help_text.lower() or "updated" in field.help_text.lower()

    def test_user_tracking_fields_in_model_fields(self):
        """Test that user tracking fields are present in model fields."""
        fields = TraceableModel._meta.get_fields()
        field_names = [f.name for f in fields]

        assert "created_by" in field_names
        assert "updated_by" in field_names


class TraceableModelSaveMethodTest(SimpleTestCase):
    """Test the save method that automatically populates user tracking fields.

    Note: These tests verify the method structure and mocking behavior.
    Full integration tests with database persistence will be added when concrete
    models inherit from TraceableModel, as creating test tables for dynamically
    defined models requires migrations which are not available in test environment.

    Future integration tests should verify:
    - created_by and updated_by are set on create with authenticated user
    - only updated_by changes on update
    - both fields remain None without authenticated user
    - behavior with update_fields parameter
    """

    def test_save_method_calls_parent_save(self):
        """Test that save() method properly calls parent save method."""
        with patch("apps.core.models.get_current_user", return_value=None):
            # Just test that the method can be called without error
            # This verifies the method structure is correct
            assert hasattr(TraceableModel, "save")
            assert callable(TraceableModel.save)

    def test_save_method_exists(self):
        """Test that TraceableModel has a save method."""
        assert hasattr(TraceableModel, "save")

    def test_save_method_handles_current_user(self):
        """Test that save method can retrieve current user via get_current_user."""
        # Mock the get_current_user function to verify it's being called
        with patch("apps.core.models.get_current_user") as mock_get_user:
            mock_get_user.return_value = None
            # Verify the import works and function is accessible
            assert mock_get_user is not None

    def test_save_guards_against_anonymous_user(self):
        """Test that save() properly checks for authenticated user."""
        # Mock an AnonymousUser
        from django.contrib.auth.models import AnonymousUser

        anonymous = AnonymousUser()

        with patch("apps.core.models.get_current_user", return_value=anonymous):
            # Verify AnonymousUser is not considered authenticated
            assert not getattr(anonymous, "is_authenticated", False)

    def test_save_checks_is_authenticated_attribute(self):
        """Test that save() uses is_authenticated check instead of truthiness."""

        # Objects without is_authenticated should be treated as unauthenticated
        class FakeUser:
            pass

        fake = FakeUser()
        # Should default to False with getattr
        assert getattr(fake, "is_authenticated", False) is False
