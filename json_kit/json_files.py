import json
from typing import Any, Iterable, Optional


def read_json_file(path: str, cls: Optional[json.JSONDecoder] = None) -> Any:
    with open(path) as file:
        return json.load(file, cls=cls)


def read_json_files(
    paths: Iterable[str], cls: Optional[json.JSONDecoder] = None
) -> Any:
    for path in paths:
        yield read_json_file(path, cls=cls)
