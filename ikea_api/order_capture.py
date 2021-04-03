from requests import Session

from .constants import Constants
from .errors import TokenExpiredError


class OrderCapture:
    """
    Part of API responsible for making an order.
    In this case used to check available delivery services.
    """

    def __init__(self, token, zip_code):
        self.zip_code = str(zip_code)
        self.session = Session()
        self.session.headers.update({
            'Accept-Encoding': Constants.ACCEPT_ENCODING,
            'Accept-Language': 'ru',
            'Origin': 'https://www.ikea.com',
            'Referer': 'https://www.ikea.com/',
            'Connection': 'keep-alive',
            'User-Agent': Constants.USER_AGENT,
            'Authorization': 'Bearer ' + token,
            'X-Client-Id': 'af2525c3-1779-49be-8d7d-adf32cac1934'
        })
        self.base_endpoint = 'https://ordercapture.ikea.ru/ordercaptureapi/ru/checkouts'

    def _call_api(self, endpoint, data=None):
        url = '{}{}'.format(self.base_endpoint, endpoint)
        if data:
            response = self.session.post(url, json=data)
        else:
            response = self.session.get(url)

        if response.status_code == 401:
            raise TokenExpiredError
        elif not response.ok:
            raise Exception(response.status_code,
                            response.content, response.headers)
        return response.json()

    def _get_checkout(self):
        data = {
            'shoppingType': 'ONLINE',
            'channel': 'WEBAPP',
            'checkoutType': 'STANDARD',
            'languageCode': 'ru',
            'preferredServiceType': None,
            'requestedServiceTypes': None
        }
        response = self._call_api('', data)
        try:
            return response['resourceId']
        except KeyError as exc:
            raise Exception(response.content) from exc

    def _get_delivery_area(self, checkout):
        endpoint = '/{}/delivery-areas'.format(checkout)
        data = {
            'zipCode': self.zip_code,
            'enableRangeOfDays': False
        }
        response = self._call_api(endpoint, data)
        try:
            return response['resourceId']
        except KeyError as exc:
            raise Exception(response.content) from exc

    def get_delivery_services(self):
        checkout = self._get_checkout()
        delivery_area = self._get_delivery_area(checkout)
        endpoint = '/{}/delivery-areas/{}/delivery-services'.format(
            checkout, delivery_area)
        response = self._call_api(endpoint)
        return response
