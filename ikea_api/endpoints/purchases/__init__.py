from ...api import API
from . import queries


class Purchases(API):
    def __init__(self, token):
        super().__init__(token, 'https://purchase-history.ocp.ingka.ikea.com/graphql')
        origin = 'https://order.ikea.com'
        self.session.headers.update({
            'Accept': '*/*',
            'Accept-Language': '{}-{}'.format(self.language_code, self.country_code),
            'Origin': origin,
            'Referer': '{}/{}/{}/purchases/'.format(
                origin, self.country_code, self.language_code)
        })

    def _build_payload(self, operation_name, query, **variables):
        payload = {
            'operationName': operation_name,
            'variables': {},
            'query': query
        }
        payload['variables'].update(variables)
        return payload

    def history(self, take=5, skip=0):
        payload = self._build_payload(
            'History', queries.history, take=take, skip=skip)
        return self.call_api(data=payload)

    def order_info(self, order_number, email=None):
        headers = {
            'Referer': '{}/{}/'.format(self.session.headers['Origin'], order_number)
        }
        payload = [
            self._build_payload('StatusBannerOrder',
                                queries.status_banner_order, orderNumber=order_number),
            self._build_payload('CostsOrder',
                                queries.costs_order, orderNumber=order_number)
        ]

        if email:
            headers['Referer'] = self.session.headers['Referer'] + 'lookup'
            for d in payload:
                d['variables']['liteId'] = email

        return self.call_api(headers=headers, data=payload)