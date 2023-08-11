import fnmatch
import glob
import gzip
import json
import os
from typing import Any, Iterable, Iterator, Optional, Union
from . import logging

logger = logging.logger


def find(
        paths: Union[str, Iterable[str]], 
        filename_patterns: Optional[str] = None, 
        files_only: bool = False) -> Iterator[str]:

    paths = [paths] if isinstance(paths, str) else paths
    filename_patterns = _prepare_filename_patterns(filename_patterns)
    for path in paths:
        files = _find(path)
        if files_only:
            files = filter(os.path.isfile, files)

        if filename_patterns:
            files = filter(lambda f: any(fnmatch.fnmatch(f, p) for p in filename_patterns), files)

        yield from files


def _prepare_filename_patterns(filename_patterns: Optional[str]) -> Optional[Iterable[str]]:
    if filename_patterns:
        return [(f'*{p}*' if '*' not in p else p) for p in filename_patterns]


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


def read_files(paths: Iterable[str]) -> Iterator[Any]:
    for path in paths:
        yield read_file(path)


def read_file(path: str) -> Any:
    logger.info(f'Reading: {path}')
    if path.endswith((".jsonl", ".jsonl.gz")):
        return read_jsonl_file(path)
    elif path.endswith((".json", ".json.gz")):
        return read_json_file(path)
    else:
        raise ValueError(f"Unsupported file extension: {path}")


def read_json_file(path: str) -> Any:
    with gzip.open(path) as file:
        return json.load(file)


def read_jsonl_file(path: str) -> Iterator[dict]:
    with open(path) as file:
        for line in file:
            if line:
                yield json.loads(line)


def replace_file_extension(path: str, old_extensions: Iterable[str], new_extension: str) -> str:
    filename = os.path.basename(path)
    directory = os.path.dirname(path)
    for old_extension in sorted(old_extensions, key=len, reverse=True):
        if old_extension in filename:
            filename = filename.replace(old_extension, new_extension)
            break
    else:
        logger.warning(f"Could not find any of the old extensions in the filename: {path} (old file extensions: {old_extensions}, new file extension: {new_extension})")
    return os.path.join(directory, filename)


def create_file(path: str, data: str):
    with open(path, "w") as f:
        f.write(data)
