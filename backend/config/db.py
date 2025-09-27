import os

import psycopg2


class DbInitializer:
    def __init__(
        self,
        dbname=None,
        user=None,
        password=None,
        host=None,
        port=None,
    ):
        # Use environment variables if provided, otherwise fallback
        self.dbname = dbname or os.environ.get("DB_NAME", "data")
        self.user = user or os.environ.get("DB_USERNAME", "username")
        self.password = password or os.environ.get("DB_PASSWORD", "password")
        self.host = host or os.environ.get("DB_HOST", "localhost")
        self.port = port or int(os.environ.get("DB_PORT", 5432))

        # Create db connection
        self.connection = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

    def get_connection(self):
        return self.connection
