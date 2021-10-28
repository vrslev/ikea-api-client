from __future__ import annotations

from typing import Any

from requests import Response
from typing_extensions import Literal, TypedDict


class CustomResponse(Response):
    _json: Any


class GraphQLResponse(TypedDict):
    data: dict[str, Any]
    errors: list[dict[str, Any]] | None


class OrderCaptureErrorDict(TypedDict):
    timestamp: int
    message: str
    detailsMap: dict[str, Any]
    errorCode: int
    details: str | None
    gaErrorList: list[dict[str, Any]] | None


SearchType = Literal["PRODUCT", "CONTENT", "PLANNER", "REFINED_SEARCHES", "ANSWER"]
