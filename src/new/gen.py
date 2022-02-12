from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Generator, ParamSpec, Protocol, TypeVar, cast

from new import abc
from new.constants import Constants, get_default_headers
from new.error_handlers import handle_401, handle_json_decode_error
from new.executors.requests import RequestsResponseData, get_session_from_session_data

Endpoint = Generator[
    abc.RequestInfo,
    abc.ResponseInfo[abc.PreparedData, Any],
    abc.Rerun[abc.PreparedData] | abc.EndpointResponse,
]


def run(
    func_gen: Callable[
        [abc.PreparedData], Endpoint[abc.PreparedData, abc.EndpointResponse]
    ],
    data: abc.PreparedData,
    session_data: abc.SessionInfo,
) -> abc.EndpointResponse:
    gen = func_gen(data)

    req_data = next(gen)
    req_data.url = session_data.base_url + req_data.url

    session = get_session_from_session_data(session_data)
    response = session.request(
        method=req_data.method,
        url=req_data.url,
        params=req_data.params,
        data=req_data.data,
        json=req_data.json,
        headers=req_data.headers,
    )

    response_info = RequestsResponseData(response)

    for handler in getattr(func_gen, "error_handlers", ()):
        handler(response_info)

    try:
        gen.send(response_info)
    except StopIteration as exc:
        parsed_response = exc.value
    else:
        raise Exception

    if isinstance(parsed_response, abc.Rerun):
        new_data = cast(abc.Rerun[abc.PreparedData], parsed_response).data
        return run(session_data=session_data, data=new_data, func_gen=func_gen)

    return parsed_response


P = ParamSpec("P")
T = TypeVar("T")


# def add_handler(handler: Callable[[abc.ResponseInfo[Any, Any]], None]):
#     def decorator(
#         func: Callable[P, Endpoint[abc.PreparedData, abc.EndpointResponse]]
#     ) -> Callable[P, Endpoint[abc.PreparedData, abc.EndpointResponse]]:
#         @wraps(func)
#         def wrapper(
#             *args: P.args, **kwargs: P.kwargs
#         ) -> Endpoint[abc.PreparedData, abc.EndpointResponse]:
#             gen = func(*args, **kwargs)
#             req_info = next(gen)
#             response_info = yield req_info
#             handler(response_info)

#             try:
#                 yield gen.send(response_info)
#             except StopIteration as exc:
#                 return exc.value
#             else:
#                 raise Exception

#             # res = yield response_info
#             # if not isinstance(res, abc.Rerun):
#             #     handler(res)  # type: ignore
#             return res  # type: ignore

#         return wrapper

#     return decorator


def add_handler(handler: Callable[[abc.ResponseInfo[Any, Any]], None]):
    def decorator(
        func: Callable[P, Endpoint[abc.PreparedData, abc.EndpointResponse]]
    ) -> Callable[P, Endpoint[abc.PreparedData, abc.EndpointResponse]]:
        if not getattr(func, "error_handlers", None):
            func.error_handlers = []
            # setattr(func, "error_handlers", [])
        func.error_handlers.append(handler)
        return func
        # @wraps(func)
        # def wrapper(
        #     *args: P.args, **kwargs: P.kwargs
        # ) -> Endpoint[abc.PreparedData, abc.EndpointResponse]:
        #     ...

        # return wrapper

    return decorator


@dataclass
class GetSomethingData:
    items: list[str]


def handle_haha(response: abc.ResponseInfo[Any, Any]):
    raise Exception("You've been Jammed!")


@dataclass
class API:
    constants: Constants
    session_info: abc.SessionInfo = field(init=False)

    def __post_init__(self) -> None:
        self.session_info = abc.SessionInfo(
            base_url="https://example.com", headers=get_default_headers(self.constants)
        )

    @add_handler(handle_haha)
    # @add_handler(handle_json_decode_error)
    def get_something(self, data: GetSomethingData) -> Endpoint[GetSomethingData, str]:
        payload = {"itemNo": i for i in data.items}
        request_info = abc.RequestInfo("GET", "/test", json=payload)

        response_info = yield request_info
        return response_info.text


api = API(Constants())
print(run(api.get_something, GetSomethingData([]), api.session_info))
