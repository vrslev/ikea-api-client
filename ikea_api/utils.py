import re
from configparser import ConfigParser
import requests
from .errors import NoItemsParsedError, WrongZipCodeError


def check_response(response):
    if not response.ok:
        raise Exception(response.status_code, response.text)


def parse_item_code(item_code):
    def parse(item_code):
        found = re.search(
            r'\d{3}[, .-]{0,2}\d{3}[, .-]{0,2}\d{2}', str(item_code))
        try:
            clean = re.sub(r'[^0-9]+', '', found[0])
        except TypeError:
            clean = None
        return clean

    if isinstance(item_code, list):
        res = []
        for i in item_code:
            parsed = parse(i)
            if parsed:
                res.append(parsed)
        if len(res) == 0:
            raise NoItemsParsedError(item_code)
        return res
    elif isinstance(item_code, str):
        parsed = parse(item_code)
        if not parsed:
            raise NoItemsParsedError(item_code)
        return parsed


def validate_zip_code(zip_code):
    if len(re.findall(r'[^0-9]', zip_code)) > 0:
        raise WrongZipCodeError(zip_code)


def get_client_id_from_home_page(country_code, language_code):
    base_url = 'https://www.ikea.com/{}/{}/'.format(
        country_code.lower(), language_code.lower())
    home_page = requests.get(base_url)
    res = re.findall(
        '"({}token-service/[^.]+.js)"'.format(base_url), home_page.text)
    if len(res) == 0:
        raise Exception
    script = requests.get(res[0])
    try:
        client_id = re.search(
            r'auth0:{[^}]+clientID:"([^"]+)"[^}]+}', script.text)[1]
        config.set(config_section, 'client_id', client_id)
        with open(config_path, 'w') as f:
            config.write(f)
    except IndexError:
        raise Exception
    return client_id


def get_client_id_from_login_page(country_code='ru', language_code='ru'):
    login_url = 'https://www.ikea.com/{}/{}/profile/login/'.format(
        country_code.lower(), language_code.lower())
    login_page = requests.get(login_url)
    res = re.findall(
        '/{}/{}/profile/app-[^/]+.js'.format(country_code, language_code), login_page.text)
    if len(res) == 0:
        raise Exception
    script = requests.get('https://www.ikea.com' + res[0])
    try:
        client_id = re.findall(
            '{DOMAIN:"%s.accounts.ikea.com",CLIENT_ID:"([^"]+)"' % country_code, script.text)[1]
        config.set(config_section, 'client_id', client_id)
        with open(config_path, 'w') as f:
            config.write(f)
    except IndexError:
        raise Exception
    return client_id


def get_config_values():
    items = dict(config.items(section=config_section))
    if not 'client_id' in items:
        client_id = get_client_id_from_login_page(
            items['country_code'], items['language_code'])
        config.set(config_section, 'client_id', client_id)
        with open(config_path, 'w') as f:
            config.write(f)

    return {
        'client_id': items['client_id'],
        'country_code': items['country_code'].lower(),
        'language_code': items['language_code'].lower()
    }


default_config = {
    'client_id': '72m2pdyUAg9uLiRSl4c4b0b2tkVivhZl',
    'country_code': 'ru',
    'language_code': 'ru'
}
config_path = 'config.ini'
config_section = 'Settings'
config = ConfigParser()
config.read(config_path)
if not config.has_section(config_section):
    config.add_section(config_section)
    for attr in default_config:
        config.set(config_section, attr, default_config[attr])
    with open(config_path, 'a+') as f:
        config.write(f)
