"""
pytest configuration for Django GIS testing with PostGIS support.

Uses a pytest fixture to enable PostGIS extensions after database creation.
"""

import pytest
from django.db import connection


@pytest.fixture(scope="session", autouse=True)
def enable_postgis(django_db_setup, django_db_blocker):
    """Enable PostGIS extensions in the test database."""
    with django_db_blocker.unblock():
        try:
            with connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology;")
                print("\n✅ PostGIS extensions enabled in test database")
        except Exception as e:
            print(f"\n⚠️  Warning: Could not enable PostGIS extensions: {e}")
