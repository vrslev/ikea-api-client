import json
from pathlib import Path
from typing import Any

from ikea_api._api import GraphQLResponse


def get_files_in_directory(dirname: str):
    return (Path(__file__).parent / "data" / dirname).glob("*")


def get_all_data_files_in_directory(dirname: str):
    res: list[Any] = []
    for path in get_files_in_directory(dirname):
        with open(path) as f:
            res.append(json.load(f))
    return res


def get_data_file(filename: str):
    path = Path(__file__).parent / "data" / filename
    with open(path) as f:
        return json.load(f)


class TestData:
    item_ingka = get_all_data_files_in_directory("item_ingka")
    item_iows = get_all_data_files_in_directory("item_iows")
    item_pip = get_all_data_files_in_directory("item_pip")
    order_capture_home = get_all_data_files_in_directory("order_capture/home")
    order_capture_collect = get_all_data_files_in_directory("order_capture/collect")
    purchases_status_banner: GraphQLResponse = get_data_file(
        "purchases/status_banner.json"
    )
    purchases_costs: GraphQLResponse = get_data_file("purchases/costs.json")
    purchases_history: GraphQLResponse = get_data_file("purchases/history.json")
