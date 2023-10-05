from page_analyzer.database import Database
from bs4 import BeautifulSoup
from page_analyzer.dto import UrlsDTO, UrlDTO, UrlsChecksDTO, ParseDTO
import requests

db = Database()


def get_all_urls():
    urls_list = db.fetchall("SELECT DISTINCT ON (urls.id) urls.id, "
                            "urls.name, "
                            "url_checks.created_at, "
                            "url_checks.status_code "
                            "FROM urls "
                            "LEFT JOIN url_checks "
                            "ON urls.id = url_checks.url_id "
                            "ORDER BY urls.id ASC;")
    result = UrlsDTO.from_list(urls_list).__dict__
    return result['urls']


def check_if_url_exists(name):
    url = db.fetchone("SELECT * FROM urls WHERE name = %s;", name)
    if not url:
        return None
    result = UrlDTO(*url)
    return result.__dict__


def get_url_by_id(url_id):
    url = db.fetchone("SELECT * FROM urls WHERE id = %s;", url_id)
    if not url:
        return None
    result = UrlDTO(*url)
    return result.__dict__


def insert_into_urls(name):
    url = db.fetchone("INSERT INTO urls (name) VALUES (%s) RETURNING *;", name)
    result = UrlDTO(*url)
    return result.__dict__


def get_url_details(url_id):
    urls_checks_list = db.fetchall("SELECT * FROM url_checks "
                                   "WHERE url_id = %s "
                                   "ORDER BY id DESC;",
                                   (url_id,)
                                   )
    result = UrlsChecksDTO.from_list(urls_checks_list).__dict__
    return result['urls']


def insert_into_urls_checks(url_id, parsed_content):
    status_code, h1, title, description = parsed_content.values()

    db.fetchone("INSERT INTO url_checks "
                "(url_id, h1, title, description, status_code) "
                "VALUES (%s, %s, %s, %s, %s) "
                "RETURNING *;",
                url_id, h1, title, description, status_code
                )


def parse_website(url_name):
    try:
        r = requests.get(url_name)
        r.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    status_code = r.status_code
    html_text = r.text

    soup = BeautifulSoup(html_text, 'html.parser')

    h1 = soup.h1.string if soup.find('h1') else ''
    title = soup.title.string if soup.find('title') else ''
    description = (
        soup.find('meta', attrs={'name': 'description'})['content']
        if (soup.find("meta", attrs={'name': 'description'}))
        else ''
    )
    parsed_data = [status_code, h1, title, description]
    result = ParseDTO(*parsed_data)

    return result
