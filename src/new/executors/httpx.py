from new.abc import EndpointInfo, EndpointResponse


async def run(endpoint: EndpointInfo[EndpointResponse]) -> EndpointResponse:
    ...
