from __future__ import annotations

from requests import Session

from ikea_api.constants import Constants, Secrets
from ikea_api.errors import ItemFetchError

from . import generic_item_fetcher


def _fetch_items_specs(session: Session, items: list[str]):
    url = (
        "https://api.ingka.ikea.com/salesitem/communications/"
        + Constants.COUNTRY_CODE
        + "/"
        + Constants.LANGUAGE_CODE
    )
    params = {"itemNos": ",".join(items)}
    response = session.get(url, params=params)
    r_json = response.json()
    if "data" not in r_json and "error" in r_json:
        err_msg = None
        if "message" in r_json["error"]:
            error = r_json["error"]
            r_err_msg = error["message"]
            if r_err_msg == "no item numbers were found":
                try:
                    err_msg = error["details"][0]["value"]["keys"]
                except (KeyError, TypeError):
                    pass
            if not err_msg:
                err_msg = r_err_msg
        else:
            err_msg = r_json["error"]
        raise ItemFetchError(err_msg)

    return r_json


def fetch(items: str | list[str]):
    headers = {
        "Accept": "*/*",
        "Referer": f"{Constants.BASE_URL}/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}/order/delivery/",
        "x-client-id": Secrets.item_ingka_x_client_id,
    }
    return generic_item_fetcher(items, headers, _fetch_items_specs, 50)
