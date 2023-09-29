from bs4 import BeautifulSoup
import requests


def parse_website(url):
    try:
        r = requests.get(url['name'])
        status_code = r.status_code
        html_text = r.text
        r.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    soup = BeautifulSoup(html_text, 'html.parser')

    h1 = soup.h1.string if soup.find('h1') else ''
    title = soup.title.string if soup.find('title') else ''
    description = (
        soup.find('meta', attrs={'name': 'description'})['content']
        if (soup.find("meta", attrs={'name': 'description'}))
        else ''
    )

    return {
        'status_code': status_code,
        'h1': h1,
        'title': title,
        'description': description
    }
