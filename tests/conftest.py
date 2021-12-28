import json
from pathlib import Path
from typing import Any


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
