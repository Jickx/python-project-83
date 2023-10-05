from page_analyzer.app import app
from flask import (
    render_template,
    request,
    flash,
    url_for,
    redirect,
    get_flashed_messages,
    abort
)
from page_analyzer.service import (
    get_all_urls,
    get_url_details,
    check_if_url_exists,
    insert_into_urls,
    insert_into_urls_checks,
    get_url_by_id
)
from urllib.parse import urlparse
from page_analyzer.service import parse_website
import validators


@app.route('/')
def home_page():
    return render_template('home.html')


@app.get('/urls')
def get_urls():
    urls = get_all_urls()
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def post_urls():
    url_req = request.form.get('url')
    if not url_req:
        flash('URL обязателен', 'danger')
        return render_template('/home.html', url=url_req), 422
    url_parsed = urlparse(url_req)
    url_norm = f'{url_parsed.scheme}://{url_parsed.netloc}'

    if not validators.url(url_norm):
        flash('Некорректный URL', 'danger')
        return render_template('/home.html', url=url_req), 422

    url = check_if_url_exists(url_norm)

    if url:
        flash('Страница уже существует', 'info')
        return redirect(url_for('url_info', url_id=url['id']), 302)

    url = insert_into_urls(url_norm)
    url_id = url['id']
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url_info', url_id=url_id), 302)


@app.route('/urls/<int:url_id>')
def url_info(url_id):
    url = get_url_by_id(url_id)
    if not url:
        abort(404)
    url_details = get_url_details(url_id)
    messages = get_flashed_messages(with_categories=True)
    return render_template('show.html',
                           messages=messages,
                           url_id=url_id,
                           url=url,
                           urls=url_details
                           ), 200


@app.post('/urls/<int:url_id>/checks')
def get_checks(url_id):
    url_name = get_url_by_id(url_id)['name']
    parsed_content = parse_website(url_name)

    if not parsed_content:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_info', url_id=url_id), 302)

    insert_into_urls_checks(url_id, parsed_content.__dict__)

    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_info', url_id=url_id), 302)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
