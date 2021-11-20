import re
import sys

import pytest


def test_pydantic_import_passes():
    import ikea_api.wrappers  # type: ignore


def test_pydantic_import_fails():
    sys.modules["pydantic"] = None  # type: ignore
    del sys.modules["ikea_api.wrappers"]
    with pytest.raises(
        RuntimeError,
        match=re.escape(
            "To use wrappers you need Pydantic to be installed. "
            + "Run 'pip install \"ikea_api[wrappers]\"' to do so."
        ),
    ):
        import ikea_api.wrappers  # type: ignore
    del sys.modules["pydantic"]
