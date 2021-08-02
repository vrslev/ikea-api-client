from typing import Any, Dict, List, Optional, Union

from ikea_api.api import API

from . import queries


class Purchases(API):
    def __init__(self, token: str):
        super().__init__(token, "https://purchase-history.ocp.ingka.ikea.com/graphql")
        origin = "https://order.ikea.com"
        self.session.headers.update(
            {
                "Accept": "*/*",
                "Accept-Language": "{}-{}".format(
                    self.language_code, self.country_code
                ),
                "Origin": origin,
                "Referer": "{}/{}/{}/purchases/".format(
                    origin, self.country_code, self.language_code
                ),
            }
        )

    def _build_payload(
        self, operation_name: str, query: str, **variables: Any
    ) -> Dict[str, Dict[str, Any]]:
        payload: Dict[str, Any] = {
            "operationName": operation_name,
            "variables": {},
            "query": query,
        }
        payload["variables"].update(variables)
        return payload

    def history(self, take: int = 5, skip: int = 0):
        """
        Get purchase history.

        Parameters are for pagination.
        If you want to see all your purchases set 'take' to 10000
        """
        payload = self._build_payload("History", queries.history, take=take, skip=skip)
        return self.call_api(data=payload)

    def order_info(self, order_number: Union[str, int], email: Optional[str] = None):
        """
        Get order information: status and costs.

        :params order_number: ID of your purchase
        :params email: Your email. If set, there's no need to get token — just pass None
        """
        order_number = str(order_number)
        headers = {
            "Referer": "{}/{}/".format(self.session.headers["Origin"], order_number)
        }
        payload: List[Dict[str, Dict[str, Any]]] = [
            self._build_payload(
                "StatusBannerOrder",
                queries.status_banner_order,
                orderNumber=order_number,
            ),
            self._build_payload(
                "CostsOrder", queries.costs_order, orderNumber=order_number
            ),
        ]

        if email:
            headers["Referer"] = self.session.headers["Referer"] + "lookup"
            for d in payload:
                d["variables"]["liteId"] = email

        return self.call_api(headers=headers, data=payload)
