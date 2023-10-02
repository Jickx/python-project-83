import psycopg2
from page_analyzer.app import app


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(app.config['DATABASE_URL'])
        self.cur = self.conn.cursor()
        self.description = None

    def query(self, query, *args):
        self.cur.execute(query, *args)
        self.description = self.cur.description

    def fetchall(self):
        return self.cur.fetchall()

    def fetchone(self):
        return self.cur.fetchone()

    def close(self):
        self.cur.close()
        self.conn.commit()
        self.conn.close()
