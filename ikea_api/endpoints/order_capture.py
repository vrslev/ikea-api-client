from ..api import Api
from ..utils import validate_zip_code
from ..errors import WrongZipCodeError


class OrderCapture(Api):
    """
    Part of API responsible for making an order.
    In this case used to check available delivery services.
    """

    def __init__(self, token, zip_code):
        super().__init__(token, 'https://ordercapture.ikea.ru/ordercaptureapi/ru/checkouts')
        if not self.country_code == 'ru':
            self.endpoint = 'https://ordercapture.ingka.com/ordercaptureapi/{}/checkouts'.format(
                self.country_code)
        self.zip_code = str(zip_code)
        validate_zip_code(zip_code)
        self.session.headers.update({
            'Accept-Language': 'ru',
            'Origin': 'https://www.ikea.com',
            'Referer': 'https://www.ikea.com/',
            'X-Client-Id': 'af2525c3-1779-49be-8d7d-adf32cac1934'
        })

    def error_handler(self, status_code, response_json):
        if 'errorCode' in response_json:
            if response_json['errorCode'] == 60004:
                raise WrongZipCodeError

    def _get_checkout(self):
        data = {
            'shoppingType': 'ONLINE',
            'channel': 'WEBAPP',
            'checkoutType': 'STANDARD',
            'languageCode': 'ru',
            'preferredServiceType': None,
            'requestedServiceTypes': None
        }
        response = self.call_api(data=data)
        if 'resourceId' in response:
            return response['resourceId']
        else:
            raise Exception('No resourceId for checkout')

    def _get_delivery_area(self, checkout):
        endpoint = '{}/{}/delivery-areas'.format(self.endpoint, checkout)
        data = {
            'zipCode': self.zip_code,
            'enableRangeOfDays': False
        }
        response = self.call_api(endpoint=endpoint, data=data)
        if 'resourceId' in response:
            return response['resourceId']
        else:
            raise Exception('No resourceId for delivery area')

    def get_delivery_services(self):
        checkout = self._get_checkout()
        delivery_area = self._get_delivery_area(checkout)
        endpoint = '{}/{}/delivery-areas/{}/delivery-services'.format(
            self.endpoint, checkout, delivery_area)
        response = self.call_api(endpoint=endpoint)
        return response
