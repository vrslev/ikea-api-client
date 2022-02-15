from typing import Callable

from new.abc import Endpoint, EndpointResponse
from new.executors.requests import execute as requests_executor


def run(
    endpoint: Endpoint[EndpointResponse],
    executor: Callable[[Endpoint[EndpointResponse]], EndpointResponse] | None = None,
) -> EndpointResponse:
    if executor is None:
        executor = requests_executor
    return executor(endpoint)
