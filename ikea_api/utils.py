import re


def check_response(response):
    if not response.ok:
        raise Exception(response.status_code, response.content)


def parse_item_code(item_code):
    found = re.search(
        r'\d{3}[, .-]{0,2}\d{3}[, .-]{0,2}\d{2}', str(item_code))
    try:
        clean = re.sub(r'[^0-9]+', '', found[0])
    except TypeError:
        clean = None
    return clean
