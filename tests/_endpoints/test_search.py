from urllib.parse import urlencode

import responses

from ikea_api._constants import Constants
from ikea_api._endpoints.search import Search


@responses.activate
def test_search():
    responses.add(
        responses.GET,
        url=f"https://sik.search.blue.cdtapps.com/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}/search-result-page",
        json={"foo": "bar"},
        match=[
            responses.matchers.query_string_matcher(  # type: ignore
                urlencode(
                    {
                        "autocorrect": "true",
                        "subcategories-style": "tree-navigation",
                        "types": "PRODUCT,PLANNER,REFINED_SEARCHES",
                        "q": "Billy",
                        "size": 10,
                        "c": "sr",
                        "v": "20210322",
                    }
                )
            )
        ],
    )

    res = Search()("Billy", limit=10, types=["PRODUCT", "PLANNER", "REFINED_SEARCHES"])
    assert res == {"foo": "bar"}
