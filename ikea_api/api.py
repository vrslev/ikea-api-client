from requests import Session
from .errors import (
    CODES_TO_ERRORS,
    TokenExpiredError,
    NotAuthenticatedError,
    TokenDecodeError
)

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'


class Api:
    def __init__(self, token, endpoint):
        self.endpoint = endpoint
        self.session = Session()
        self.session.headers.update({
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'User-Agent': USER_AGENT,
            'Authorization': 'Bearer ' + token
        })

    def error_handler(self, status_code, response_json):
        pass

    def basic_error_handler(self, status_code, response_json):
        err = None
        if 'error' in response_json:
            err = response_json['error']
            if isinstance(err, str):
                if status_code == 401:
                    if err == 'Token has expired':
                        raise TokenExpiredError
                    elif err == 'Token could not be decoded':
                        raise TokenDecodeError
                    else:
                        raise NotAuthenticatedError(response_json['error'])

        if isinstance(response_json, list):
            if isinstance(response_json[0], dict):
                if 'errors' in response_json[0]:
                    err = response_json[0]['errors']
        if isinstance(response_json, dict):
            if 'errors' in response_json:
                err = response_json['errors']
        if err:
            if isinstance(err, list):
                err = err[0]
            if 'extensions' in err:
                ext = err['extensions']
                if 'errorCode' in ext:
                    if ext['errorCode'] == 401:
                        raise NotAuthenticatedError
                elif 'code' in ext:
                    code = ext['code']
                    if code in CODES_TO_ERRORS:
                        raise CODES_TO_ERRORS[code](err)
                    else:
                        raise Exception(code + ', ' + str(err))
            else:
                if 'message' in err:
                    raise Exception(err['message'])
                else:
                    raise Exception(err)

    def call_api(self, endpoint=None, headers=None, data=None):
        """Call one of IKEA's API"""
        if not endpoint:
            endpoint = self.endpoint
        if data:
            response = self.session.post(endpoint, headers=headers, json=data)
        else:
            response = self.session.get(endpoint, headers=headers)
        response_json = response.json()
        self.basic_error_handler(response.status_code, response_json)
        self.error_handler(response.status_code, response_json)
        if not response.ok:
            raise Exception(response.status_code, response.text)

        return response_json
