from ikea_api.constants import Constants
from ikea_api.endpoints import search
from tests.conftest import EndpointTester


def test_search(constants: Constants):
    query = "myquery"
    limit = 30
    types: list[search.SearchType] = ["PLANNER", "REFINED_SEARCHES"]

    t = EndpointTester(search.Search(constants).search(query, limit=limit, types=types))
    req = t.prepare()

    assert req.params
    assert req.params["types"] == ",".join(types)
    assert req.params["q"] == query
    assert req.params["size"] == limit

    t.assert_json_returned()
