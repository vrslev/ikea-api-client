import sys

import pytest


def test_no_pydantic():
    sys.modules["pydantic"] = None  # type: ignore
    del sys.modules["ikea_api"]
    import ikea_api

    with pytest.raises(AttributeError):
        ikea_api.get_items

    del sys.modules["pydantic"]
