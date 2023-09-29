from flask import (
    Flask,
    render_template,
    request,
    flash,
    url_for,
    redirect,
    get_flashed_messages,
    abort
)
from dotenv import load_dotenv
from urllib.parse import urlparse
from .parse import parse_website
import psycopg2
import os
import validators

load_dotenv()
app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


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


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


@app.route('/')
def home_page():
    return render_template('home.html')


@app.get('/urls')
def urls_page():
    urls = get_all_urls()
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def post_url():
    url_req = request.form.get('url')
    if not url_req:
        flash('URL обязателен', 'danger')
        return render_template('/home.html', url=url_req), 422
    url_parsed = urlparse(url_req)
    url_norm = f'{url_parsed.scheme}://{url_parsed.netloc}'

    if not validators.url(url_norm):
        flash('Некорректный URL', 'danger')
        return render_template('/home.html', url=url_req), 422

    url = get_url_by_name(url_norm)

    if url:
        flash('Страница уже существует', 'info')
        return redirect(url_for('get_url_details', id=url['id']), 302)

    id = insert_into_urls(url_norm)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('get_url_details', id=id), 302)


@app.route('/urls/<int:id>')
def get_url_details(id):
    url = get_url_by_id(id)
    if not url:
        abort(404)
    url_details = get_all_url_details(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template('show.html',
                           messages=messages,
                           id=id,
                           url=url,
                           urls=url_details
                           ), 200


@app.post('/urls/<id>/checks')
def get_checks(id):
    url = get_url_by_id(id)
    parsed_content = parse_website(url)

    if not parsed_content:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_url_details', id=id), 302)

    insert_into_urls_checks(id, parsed_content)

    flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_url_details', id=id), 302)
