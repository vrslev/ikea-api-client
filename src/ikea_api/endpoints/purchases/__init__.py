from typing import Any, Dict, List, Optional, Union

from ikea_api.api import API
from ikea_api.constants import Constants

from . import queries


class Purchases(API):
    def __init__(self, token: str):
        super().__init__(token, "https://purchase-history.ocp.ingka.ikea.com/graphql")
        origin = "https://order.ikea.com"
        self._session.headers.update(
            {
                "Accept": "*/*",
                "Accept-Language": Constants.LANGUAGE_CODE
                + "-"
                + Constants.COUNTRY_CODE,
                "Origin": origin,
                "Referer": f"{origin}/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}/purchases/",
            }
        )

    def _build_payload(
        self, operation_name: str, query: str, **variables: Any
    ) -> Dict[str, Dict[str, Any]]:
        payload: Dict[str, Any] = {
            "operationName": operation_name,
            "variables": {**variables},
            "query": query,
        }
        return payload

    def history(self, take: int = 5, skip: int = 0):
        """
        Get purchase history.

        Parameters are for pagination.
        If you want to see all your purchases set 'take' to 10000
        """
        payload = self._build_payload("History", queries.history, take=take, skip=skip)
        return self._call_api(data=payload)

    def order_info(self, order_number: Union[str, int], email: Optional[str] = None):
        """
        Get order information: status and costs.

        :params order_number: ID of your purchase
        :params email: Your email. If set, there's no need to get token — just pass None
        """
        order_number = str(order_number)
        headers = {"Referer": f"{self._session.headers['Origin']}/{order_number}/"}
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
            headers["Referer"] = self._session.headers["Referer"] + "lookup"
            for d in payload:
                d["variables"]["liteId"] = email

        return self._call_api(headers=headers, data=payload)
