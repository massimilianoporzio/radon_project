"""
pytest configuration for Django GIS testing with PostGIS support.

Patches Django's MigrationExecutor to enable PostGIS before migrations run.
"""


def pytest_configure(config):
    """
    Intercept Django's migration executor to enable PostGIS BEFORE migrations run.
    """
    from django.db.migrations.executor import MigrationExecutor

    original_init = MigrationExecutor.__init__

    def patched_init(self, connection, progress_callback=None):
        """
        Initialize executor and enable PostGIS extensions before any migrations.
        """
        # First, enable PostGIS on this connection
        db_name = connection.settings_dict.get("NAME", "")
        if "test" in db_name.lower():
            try:
                with connection.cursor() as cursor:
                    cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
                    cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology;")
            except Exception:
                pass  # Silently ignore

        # Now call original init
        return original_init(self, connection, progress_callback)

    MigrationExecutor.__init__ = patched_init
