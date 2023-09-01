from flask import (
    Flask,
    render_template,
    request,
    flash,
    url_for,
    redirect,
    get_flashed_messages
)
from dotenv import load_dotenv
import psycopg2
import os
import validators
from url_normalize import url_normalize
import secrets
import requests

import logging

app = Flask(__name__)
load_dotenv()

secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


def connect_to_db():
    conn = psycopg2.connect(app.config['DATABASE_URL'])
    return conn


def get_all_urls():
    conn = connect_to_db()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT ON (urls.id) urls.id, "
                        "urls.name, "
                        "url_checks.status_code, "
                        "url_checks.created_at "
                        "FROM urls "
                        "LEFT JOIN url_checks ON urls.id = url_checks.url_id "
                        "ORDER BY urls.id ASC")
            column_names = [desc[0] for desc in cur.description]
            result = cur.fetchall()
    conn.close()
    return map(lambda x: dict(zip(column_names, x)), result)


def get_url_by_name(name):
    conn = connect_to_db()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM urls WHERE name LIKE %s", (name,))
            result = cur.fetchone()
    conn.close()
    return result


def get_url_by_id(id):
    conn = connect_to_db()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
            column_names = [desc[0] for desc in cur.description]
            logging.critical(column_names)
            result = cur.fetchone()
    conn.close()
    return dict(zip(column_names, result))


def insert_data(name):
    conn = connect_to_db()
    with conn:
        with conn.cursor() as cur:
            sql = "INSERT INTO urls (name) VALUES (%s);"
            cur.execute(sql, (name,))
        conn.commit()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM urls "
                        "WHERE name LIKE %s",
                        (name,))
            id = cur.fetchone()[0]
    conn.close()
    return id


def get_all_url_details(id):
    conn = connect_to_db()
    with conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC',
                        (id,)
                        )
            column_names = [desc[0] for desc in cur.description]
            result = cur.fetchall()
    conn.close()
    return map(lambda x: dict(zip(column_names, x)), result)


def make_check(id):
    url = get_url_by_id(id)
    data = scrape(url['name'])
    conn = connect_to_db()
    with conn:
        with conn.cursor() as cur:
            sql = 'INSERT INTO url_checks (url_id, status_code) VALUES (%s, %s);'
            cur.execute(sql, (id, data,))
    conn.commit()
    conn.close()


def scrape(name):
    r = requests.get(name)
    return r.status_code


@app.route('/')
def home_page():
    messages = get_flashed_messages(with_categories=True)
    urls = get_all_urls()
    return render_template('/home.html', urls=urls, messages=messages)


@app.get('/urls')
def urls_page():
    urls = get_all_urls()
    return render_template('/urls.html', urls=urls)


@app.post('/urls')
def post_url():
    url = request.form.get('url')
    if not validators.url(url):
        flash('Некорректный URL', 'danger')
        return redirect(url_for('home_page')), 302
    url_norm = url_normalize(url)
    url = get_url_by_name(url_norm)

    if url:
        flash('Страница уже существует', 'info')
        return redirect(url_for('home_page'), 302)

    flash('Страница успешно добавлена', 'success')
    id = insert_data(url_norm)
    return redirect(url_for('get_url_details', id=id), 302)


@app.route('/urls/<int:id>')
def get_url_details(id):
    url = get_url_by_id(id)
    url_details = get_all_url_details(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template('/show.html',
                           id=id,
                           url=url,
                           urls=url_details,
                           messages=messages
                           )


@app.post('/urls/<id>/checks')
def get_checks(id):
    make_check(id)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_url_details', id=id), 302)
