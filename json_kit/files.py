import glob
import os
from typing import Iterable, Iterator, Union
import logging


logger = logging.getLogger(__name__)


def iter_paths(
        paths: Union[str, Iterable[str]], 
        files_only: bool = False,
        directories_only: bool = False) -> Iterator[str]:

    paths = [paths] if isinstance(paths, str) else paths
    for path in paths:
        files = _iter_paths(path)
        if files_only:
            files = filter(os.path.isfile, files)

        if directories_only:
            files = filter(os.path.isdir, files)
        yield from files


def _iter_paths(path: str) -> Iterator[str]:
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
