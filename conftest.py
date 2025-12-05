"""
pytest configuration for Django GIS testing with PostGIS support.

This file enables PostGIS extensions in the test database BEFORE migrations.
"""

from django.db.backends.postgresql.base import DatabaseCreation


def pytest_configure():
    """Patch Django's test database creation to enable PostGIS before migrations."""
    original_create_test_db = DatabaseCreation._create_test_db

    def _create_test_db_with_postgis(self, verbosity, autoclobber, keepdb=False):
        """Create test database and immediately enable PostGIS BEFORE migrations."""
        # Call the original method to create the database
        original_create_test_db(self, verbosity, autoclobber, keepdb)

        # Enable PostGIS extensions IMMEDIATELY after database creation
        # This happens BEFORE any migrations are run
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology;")
            if verbosity >= 2:
                test_db_name = self.connection.settings_dict["NAME"]
                print(f"\n✅ PostGIS extensions enabled in test database '{test_db_name}'")
        except Exception as e:
            if verbosity >= 1:
                print(f"\n⚠️  PostGIS extension warning: {e}")

    # Monkey-patch the internal method that creates the database
    DatabaseCreation._create_test_db = _create_test_db_with_postgis
