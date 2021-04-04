from .errors import TokenExpiredError, NotAuthenticatedError
import re


def check_response(response):
    if not response.ok:
        raise Exception(response.status_code, response.content)


def call_api(self, data):
    """Call one of IKEA's GraphQL API"""
    response = self.session.post(self.endpoint, json=data)
    response_json = response.json()
    if 'errors' in response_json:
        if 'extensions' in response_json['errors'][0]:
            if 'errorCode' in response_json['errors'][0]['extensions']:
                if response_json['errors'][0]['extensions']['errorCode'] == 401:
                    raise NotAuthenticatedError
        else:
            if 'message' in response_json['errors'][0]:
                raise Exception(response_json['errors'][0]['message'])
            else:
                raise Exception(response_json['errors'][0])
    if response.status_code == 401 and 'error' in response_json:
        if response_json['error'] == 'Token has expired':
            raise TokenExpiredError
        else:
            raise NotAuthenticatedError(response_json['error'])
    check_response(response)
    return response_json


def parse_item_code(item_code):
    found = re.search(
        r'\d{3}[,.-]{0,2}\d{3}[,.-]{0,2}\d{2}', str(item_code))
    try:
        clean = re.sub(r'[^0-9]+', '', found[0])
    except TypeError:
        clean = None
    return clean
