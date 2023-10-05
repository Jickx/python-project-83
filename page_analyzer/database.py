from contextlib import contextmanager
import psycopg2.pool
from page_analyzer.app import app


class Database:
    def __init__(self):
        self.pool = psycopg2.pool.SimpleConnectionPool(
            1,
            20,
            app.config['DATABASE_URL']
        )

    @contextmanager
    def get_cursor(self):
        conn = self.pool.getconn()
        try:
            yield conn.cursor()
            conn.commit()
        finally:
            self.pool.putconn(conn)

    def fetchall(self, query, *args):
        with self.get_cursor() as cursor:
            if args:
                cursor.execute(query, (args,))
            else:
                cursor.execute(query)
            result = cursor.fetchall()
        return result

    def fetchone(self, query, *args):
        with self.get_cursor() as cursor:
            cursor.execute(query, tuple(args))
            result = cursor.fetchone()
        return result
