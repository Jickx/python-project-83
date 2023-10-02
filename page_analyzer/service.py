from page_analyzer.database import Database


def get_all_urls():
    db = Database()
    db.query("SELECT DISTINCT ON (urls.id) urls.id, "
             "urls.name, "
             "url_checks.status_code, "
             "url_checks.created_at "
             "FROM urls "
             "LEFT JOIN url_checks ON urls.id = url_checks.url_id "
             "ORDER BY urls.id ASC")
    column_names = [desc[0] for desc in db.description]
    result = db.fetchall()
    db.close()

    return map(lambda x: dict(zip(column_names, x)), result)


def get_url_by_name(name):
    db = Database()
    db.query("SELECT * FROM urls WHERE name = %s", (name,))
    column_names = [desc[0] for desc in db.description]
    result = db.fetchone()
    db.close()
    if result:
        return dict(zip(column_names, result))
    else:
        return None


def get_url_by_id(id):
    db = Database()
    db.query("SELECT * FROM urls WHERE id = %s", (id,))
    result = db.fetchone()
    if not result:
        return None
    column_names = [desc[0] for desc in db.description]
    db.close()
    return dict(zip(column_names, result))


def insert_into_urls(name):
    db = Database()
    sql = "INSERT INTO urls (name) VALUES (%s);"
    db.query(sql, (name,))
    db.query("SELECT id FROM urls "
             "WHERE name = %s",
             (name,))
    id = db.fetchone()[0]
    db.close()
    return id


def insert_into_urls_checks(id, parsed_content):
    status_code, h1, title, description = parsed_content.values()
    db = Database()
    sql = ('INSERT INTO url_checks '
           '(url_id, h1, title, description, status_code) '
           'VALUES (%s, %s, %s, %s, %s);')
    db.query(sql, (id, h1, title, description, status_code))
    db.close()


def get_all_url_details(id):
    db = Database()
    db.query('SELECT * FROM url_checks '
             'WHERE url_id = %s '
             'ORDER BY id DESC',
             (id,)
             )
    column_names = [desc[0] for desc in db.description]
    result = db.fetchall()
    db.close()
    return map(lambda x: dict(zip(column_names, x)), result)
