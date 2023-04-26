import glob
import os
from typing import Iterable, Iterator, Union


def find(paths: Union[str, Iterable[str]], files_only: bool = False) -> Iterator[str]:
    paths = [paths] if isinstance(paths, str) else paths
    for path in paths:
        files = _find(path)
        if files_only:
            files = filter(os.path.isfile, files)
        yield from files


def _find(path: str) -> Iterator[str]:
    if "*" in path:
        paths = glob.glob(path)
    else:
        paths = [path]
    for path in paths:
        yield path
        if os.path.isdir(path):
            for directory, _, filenames in os.walk(path):
                for filename in filenames:
                    path = os.path.join(directory, filename)
                    yield path
