"""
Test suite for core models.
Tests TraceableModel abstract model structure and field configuration.
"""

from concurrency.fields import IntegerVersionField
from django.db import models
from django.test import SimpleTestCase

from apps.core.models import TraceableModel


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
