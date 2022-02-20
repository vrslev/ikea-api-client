from ikea_api.constants import Constants
from ikea_api.endpoints.search import Search, SearchType
from tests.conftest import EndpointTester


def test_search(constants: Constants):
    query = "myquery"
    limit = 30
    types: list[SearchType] = ["PLANNER", "REFINED_SEARCHES"]

    t = EndpointTester(Search(constants).search(query, limit=limit, types=types))
    req = t.prepare()

    assert req.params
    assert req.params["types"] == ",".join(types)
    assert req.params["q"] == query
    assert req.params["size"] == limit

    t.assert_json_returned()
