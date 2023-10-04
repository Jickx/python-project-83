from page_analyzer.database import Database
from dataclasses import dataclass
import datetime

db = Database()


@dataclass
class UrlDTO:
    id: int
    name: str
    created_at: datetime.datetime
    status_code: int = None


@dataclass
class UrlsDTO:
    urls: list[UrlDTO]

    @staticmethod
    def from_list(urls_list):
        return UrlsDTO([UrlDTO(*item) for item in urls_list])


@dataclass
class UrlCheckDTO:
    id: int
    url_id: int
    status_code: int
    h1: str
    title: str
    description: str
    created_at: datetime.datetime


@dataclass
class UrlsChecksDTO:
    urls: list[UrlCheckDTO]

    @staticmethod
    def from_list(urls_list):
        return UrlsChecksDTO([UrlCheckDTO(*item) for item in urls_list])


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
