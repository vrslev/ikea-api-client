from configparser import ConfigParser
import re

import requests

from .constants import Constants
from .errors import NoItemsParsedError, WrongZipCodeError


def check_response(response) -> None:
    if not response.ok:
        raise Exception(response.status_code, response.text)


def parse_item_code(item_code):
    def parse(item_code):
        found = re.search(r"\d{3}[, .-]{0,2}\d{3}[, .-]{0,2}\d{2}", str(item_code))
        res = ""
        if found:
            try:
                res = re.sub(r"[^0-9]+", "", found[0])
            except TypeError:
                pass
        return res

    if isinstance(item_code, list):
        res = []
        for i in item_code:
            parsed = parse(i)
            if parsed:
                res.append(parsed)
        if len(res) == 0:
            raise NoItemsParsedError(item_code)
        return res
    elif isinstance(item_code, (str, int)):
        parsed = parse(item_code)
        if not parsed:
            raise NoItemsParsedError(item_code)
        return parsed
    else:
        return ""


def validate_zip_code(zip_code):
    if len(re.findall(r"[^0-9]", zip_code)) > 0:
        raise WrongZipCodeError(zip_code)


def get_client_id_from_login_page(country_code="ru", language_code="ru"):
    login_url = "{}/{}/{}/profile/login/".format(
        Constants.BASE_URL, country_code.lower(), language_code.lower()
    )
    login_page = requests.get(login_url)
    res = re.findall(
        f"/{country_code}/{language_code}/profile/app-[^/]+.js",
        login_page.text,
    )
    if len(res) == 0:
        raise Exception
    script = requests.get(Constants.BASE_URL + res[0])

    client_id = re.findall(
        '{DOMAIN:"%s.accounts.ikea.com",CLIENT_ID:"([^"]+)"' % country_code, script.text
    )[1]
    return client_id


config_path = "config.ini"
config_section = "Settings"


def get_config():
    default_config = {
        "client_id": "72m2pdyUAg9uLiRSl4c4b0b2tkVivhZl",
        "country_code": "ru",
        "language_code": "ru",
    }

    config = ConfigParser()
    config.read(config_path)

    if not config.has_section(config_section):
        config.add_section(config_section)
        for attr in default_config:
            config.set(config_section, attr, default_config[attr])
        with open(config_path, "a+") as f:
            config.write(f)

    return config


def get_config_values():
    config = get_config()
    items = dict(config.items(section=config_section))
    if not "client_id" in items:
        client_id = get_client_id_from_login_page(
            items["country_code"], items["language_code"]
        )
        config.set(config_section, "client_id", client_id)
        with open(config_path, "a+") as f:
            config.write(f)

    items = dict(config.items(section=config_section))

    return {
        "client_id": items["client_id"],
        "country_code": items["country_code"].lower(),
        "language_code": items["language_code"].lower(),
    }
