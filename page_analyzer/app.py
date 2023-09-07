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
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import psycopg2
import os
import validators
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
            cur.execute('SELECT * FROM url_checks '
                        'WHERE url_id = %s '
                        'ORDER BY id DESC',
                        (id,)
                        )
            column_names = [desc[0] for desc in cur.description]
            result = cur.fetchall()
    conn.close()
    return map(lambda x: dict(zip(column_names, x)), result)


@app.route('/')
def home_page():
    return render_template('/home.html')


@app.get('/urls')
def urls_page():
    urls = get_all_urls()
    return render_template('/urls.html', urls=urls)


@app.post('/urls')
def post_url():
    url_req = request.form.get('url')
    if not url_req:
        flash('URL обязателен', 'danger')
        return render_template('/home.html'), 422
    url_parsed = urlparse(url_req)
    url_norm = f'{url_parsed.scheme}://{url_parsed.netloc}'
    if not validators.url(url_norm):
        flash('Некорректный URL', 'danger')
        return render_template('/home.html'), 422

    url = get_url_by_name(url_norm)

    if url:
        flash('Страница уже существует', 'info')
        return render_template('/home.html'), 422

    id = insert_data(url_norm)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('get_url_details', id=id), 302)


@app.route('/urls/<int:id>')
def get_url_details(id):
    url = get_url_by_id(id)
    url_details = get_all_url_details(id)
    return render_template('/show.html',
                           id=id,
                           url=url,
                           urls=url_details,
                           ), 200


@app.post('/urls/<id>/checks')
def get_checks(id):
    url = get_url_by_id(id)
    try:
        r = requests.get(url['name'])
        status_code = r.status_code
        html_text = r.text
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_url_details', id=id), 302)

    soup = BeautifulSoup(html_text, 'html.parser')

    if soup.find('h1'):
        h1 = soup.h1.string
    else:
        h1 = ''
    if soup.find('title'):
        title = soup.title.string
    else:
        title = ''
    if soup.find("meta", attrs={"name": "description"}):
        description = soup.find(
            "meta",
            attrs={"name": "description"}
        )['content']
    else:
        description = ''

    conn = connect_to_db()
    with conn:
        with conn.cursor() as cur:
            sql = ('INSERT INTO url_checks '
                   '(url_id, h1, title, description, status_code) '
                   'VALUES (%s, %s, %s, %s, %s);')
            cur.execute(sql, (id, h1, title, description, status_code, ))
    conn.commit()
    conn.close()
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_url_details', id=id), 302)
