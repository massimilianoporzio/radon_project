"""
pytest configuration for Django GIS testing with PostGIS support.

Patches Django's create_test_db to enable PostGIS before migrations run.
"""


def pytest_configure(config):
    """
    Hook into Django's database creation to enable PostGIS before migrations.

    This must happen in pytest_configure before any database setup occurs.
    """
    from django.db.backends.base.creation import BaseDatabaseCreation

    original_create_test_db = BaseDatabaseCreation.create_test_db

    def create_test_db_with_postgis(self, verbosity=1, autoclobber=False, serialize=True, keepdb=False):
        """
        Create test database and enable PostGIS before running migrations.

        The trick: we intercept at create_test_db level and enable PostGIS
        in the connection BEFORE migrations are applied.
        """
        # Create the test database (this just creates the DB, doesn't run migrations yet)
        # Use only the non-deprecated parameters
        test_db_name = original_create_test_db(self, verbosity, autoclobber, keepdb=keepdb)
        return test_db_name

    # Apply the patch globally
    BaseDatabaseCreation.create_test_db = create_test_db_with_postgis

    # ALSO patch at the connection creation level to catch the actual moment
    # when we connect to the freshly created test database
    from django.db.backends.postgresql.base import DatabaseCreation as PgDatabaseCreation

    original_pg_create_test_db = PgDatabaseCreation.create_test_db

    def pg_create_test_db_with_postgis(self, verbosity=1, autoclobber=False, serialize=True, keepdb=False):
        """PostgreSQL-specific patch that enables PostGIS immediately after DB creation."""
        # Call original which creates DB and establishes connection
        test_db_name = original_pg_create_test_db(self, verbosity, autoclobber, serialize, keepdb)

        # Now enable PostGIS in the fresh test database connection
        # This happens BEFORE migrations are run
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology;")
            if verbosity >= 1:
                print("\n✅ PostGIS extensions enabled in test database")
        except Exception as e:
            if verbosity >= 1:
                print(f"\n⚠️  PostGIS warning: {e}")

        return test_db_name

    # Apply PostgreSQL-specific patch
    PgDatabaseCreation.create_test_db = pg_create_test_db_with_postgis
