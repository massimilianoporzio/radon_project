"""
pytest configuration for Django GIS testing with PostGIS support.

This file enables PostGIS extensions in the test database after creation.
"""

from django.db import connection
from django.db.backends.postgresql.base import DatabaseCreation


def pytest_configure():
    """Patch Django's test database creation to enable PostGIS."""
    original_create_test_db = DatabaseCreation.create_test_db

    def create_test_db_with_postgis(self, verbosity=1, autoclobber=False, serialize=True, keepdb=False):
        """Create test database and enable PostGIS extensions."""
        test_db_name = original_create_test_db(self, verbosity, autoclobber, serialize, keepdb)

        # Enable PostGIS extensions in the newly created test database
        try:
            with connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology;")
            if verbosity >= 2:
                print("\n✅ PostGIS extensions enabled in test database")
        except Exception as e:
            if verbosity >= 1:
                print(f"\n⚠️  PostGIS extension warning: {e}")

        return test_db_name

    # Monkey-patch the method
    DatabaseCreation.create_test_db = create_test_db_with_postgis
