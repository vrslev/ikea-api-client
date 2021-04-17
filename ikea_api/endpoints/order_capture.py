from ..api import Api


class OrderCapture(Api):
    """
    Part of API responsible for making an order.
    In this case used to check available delivery services.
    """

    def __init__(self, token, zip_code):
        super().__init__(token, 'https://ordercapture.ikea.ru/ordercaptureapi/ru/checkouts')
        self.zip_code = str(zip_code)
        self.session.headers.update({
            'Accept-Language': 'ru',
            'Origin': 'https://www.ikea.com',
            'Referer': 'https://www.ikea.com/',
            'X-Client-Id': 'af2525c3-1779-49be-8d7d-adf32cac1934'
        })

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
        try:
            return response['resourceId']
        except KeyError as exc:
            raise Exception(response.content) from exc

    def _get_delivery_area(self, checkout):
        endpoint = '{}/{}/delivery-areas'.format(self.endpoint, checkout)
        data = {
            'zipCode': self.zip_code,
            'enableRangeOfDays': False
        }
        response = self.call_api(endpoint=endpoint, data=data)
        try:
            return response['resourceId']
        except KeyError as exc:
            raise Exception(response.content) from exc

    def get_delivery_services(self):
        checkout = self._get_checkout()
        delivery_area = self._get_delivery_area(checkout)
        endpoint = '{}/{}/delivery-areas/{}/delivery-services'.format(
            self.endpoint, checkout, delivery_area)
        response = self.call_api(endpoint=endpoint)
        return response
