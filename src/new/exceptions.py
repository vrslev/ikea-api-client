from __future__ import annotations

from typing import Any

from new.abc import ResponseInfo


class IKEAAPIError(Exception):
    """Generic API related exception."""

    response: ResponseInfo[Any, Any]

    def __init__(self, response: ResponseInfo[Any, Any], msg: Any = None):
        self.response = response
        if msg is None:
            msg = (response.status_code, response.text)
        super().__init__(msg)
