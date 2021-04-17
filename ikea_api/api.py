from requests import Session

from .utils import check_response
from .constants import Constants
from .errors import TokenExpiredError, NotAuthenticatedError


class Api:
    def __init__(self, token, endpoint):
        self.endpoint = endpoint
        self.session = Session()
        self.session.headers.update({
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'User-Agent': Constants.USER_AGENT,
            'Authorization': 'Bearer ' + token
        })

    def call_api(self, endpoint=None, headers=None, data=None):
        """Call one of IKEA's API"""
        if not endpoint:
            endpoint = self.endpoint
        if data:
            response = self.session.post(endpoint, headers=headers, json=data)
        else:
            response = self.session.get(endpoint, headers=headers)
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
        if response.status_code == 401:
            if 'error' in response_json:
                if response_json['error'] == 'Token has expired':
                    raise TokenExpiredError
                else:
                    raise NotAuthenticatedError(response_json['error'])
            else:
                raise TokenExpiredError
        check_response(response)
        return response_json
