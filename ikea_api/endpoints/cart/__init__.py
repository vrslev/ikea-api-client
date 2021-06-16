from functools import wraps
from ...api import API
from ...utils import parse_item_code
from . import queries, mutations


class Cart(API):
    """API for managing cart"""

    def __init__(self, token):
        super().__init__(token, 'https://cart.oneweb.ingka.com/graphql')
        self.session.headers['X-Client-Id'] = '66e4684a-dbcb-499c-8639-a72fa50ac0c3'

    def _build_payload(self, query, **variables):
        payload = {
            'query': query,
            'variables': {
                'languageCode': self.language_code,
                **variables
            }
        }
        payload['variables'].update(variables)
        return payload

    def _build_payload_and_call(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            res = func(self, *args, **kwargs)
            if isinstance(res, tuple):
                query, variables = res
            else:
                query, variables = res, {}
            return self.call_api(
                data=self._build_payload(query, **variables))
        return inner

    def make_templated_items(self, items):
        items_templated = []
        for item_code, qty in items.items():
            item_code = parse_item_code(item_code)
            if item_code:
                items_templated.append({'itemNo': item_code, 'quantity': qty})
        return items_templated

    @_build_payload_and_call
    def show(self):
        return queries.cart

    @_build_payload_and_call
    def clear(self):
        return mutations.clear_items

    @_build_payload_and_call
    def add_items(self, items: list[dict]):
        """
        Add items to cart.
        Required items list format: [{'item_no': quantity, ...}]
        """
        items_templated = self.make_templated_items(items)
        return mutations.add_items, {'items': items_templated}

    @_build_payload_and_call
    def update_items(self, items: list[dict]):
        """
        Replace quantity for given item to the new one.
        Required items list format: [{'item_no': quantity, ...}]
        """
        items_templated = self.make_templated_items(items)
        return mutations.update_items, {'items': items_templated}

    @_build_payload_and_call
    def copy_items(self, source_user_id):
        """Copy cart from another account"""
        return mutations.copy_items, {'sourceUserId': source_user_id}

    @_build_payload_and_call
    def remove_items(self, item_codes: list):
        """
        Remove items by item codes.
        """
        items_parsed = parse_item_code(item_codes)
        return mutations.remove_items, {'itemNos': items_parsed}

    @_build_payload_and_call
    def set_coupon(self, code: str):
        return mutations.set_coupon, {'code': code}

    @_build_payload_and_call
    def clear_coupon(self):
        return mutations.clear_coupon
