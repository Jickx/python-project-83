from dataclasses import dataclass
import datetime


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


@dataclass
class ParseDTO:
    status_code: int
    h1: str
    title: str
    description: str
