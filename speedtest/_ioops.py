"""Reading and writing the cache."""

import importlib
import os
import sys
import json
import itertools as it
import csv
import configparser
from pathlib import Path
from typing import Any, Optional, Dict
import warnings

from speedtest._stringify import stringify_time


def _get_cache_file_name(prefix: str = "run", suffix: str = ".csv") -> str:
    """Gets an appropriate cache file name. Increments until valid file name achieved."""
    cche_file = f"{prefix}{suffix}"
    inc = 1
    while os.path.isfile(os.path.join(os.getcwd(), cche_file)):
        cche_file = f"{prefix}{inc}{suffix}"
        inc += 1
    return cche_file


def read_cache(cache_name: str = "cache.json", cache_dir: Optional[str] = None) -> Dict[str, Any]:
    """Loads a cache directory at `.speedtest_cache`.

    Retrieves stored data and autorange values.
    """
    if cache_dir is None:
        cache_dir = os.path.join(os.getcwd(), ".speedtest_cache")
    
    cche_file = os.path.join(cache_dir, cache_name)

    if not os.path.isdir(cache_dir) or not os.path.isfile(cche_file):
        return {}

    with open(cche_file, "rt", encoding="utf-8") as cfile:
        data = json.load(cfile)
    return data


def read_ini(cache_name: str = "speedtest.ini", cache_dir: Optional[str] = None) -> Dict[str, Any]:
    """Loads configurations from a .ini file."""
    cfg = configparser.ConfigParser()

    if cache_dir is None:
        cache_dir = os.getcwd()

    cfg.read(os.path.join(cache_dir, cache_name))

    sections = cfg.sections()
    if "speedtest" not in sections:
        return {}

    results = {}

    params_bool = ["parallel", "tocsv", "totxt", "ignore_cache", "no_cache"]
    params_int = ["nreps", "print_pad_width"]
    params_str = ["file_or_dir", "unit"]

    for p in params_bool:
        if p in cfg["speedtest"]:
            results[p] = cfg.getboolean("speedtest", p)
    for p in params_int:
        if p in cfg["speedtest"]:
            results[p] = cfg.getint("speedtest", p)
    for p in params_str:
        if p in cfg["speedtest"]:
            results[p] = cfg.get("speedtest", p)
    return results


def write_cache(
    writable_speedtest_cache: Dict[str, Any], cache_name: str = "cache.json", indent: bool = True
) -> None:
    """Creates a cache directory at `.speedtest_cache`.

    Stores data including function names, autorange values to accelerate repeated runs.
    """
    i = 4 if indent else None
    cache_dir = os.path.join(os.getcwd(), ".speedtest_cache")
    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)

    cche_file = os.path.join(cache_dir, cache_name)
    with open(cche_file, "wt", encoding="utf-8") as cfile:
        json.dump(writable_speedtest_cache, cfile, indent=i)


def write_csv(writable_speedtest_cache: Dict[str, Any]) -> str:
    """Creates a CSV file."""
    cche_file = _get_cache_file_name("run", ".csv")

    # extract all unique parameters.
    params = [
        [[k for k in j.keys() if k.startswith("param__")] for j in i.values()]
        for i in writable_speedtest_cache.values()
    ]
    # flatten params into 1d list
    for _ in range(2):
        params = list(it.chain.from_iterable(params))
    # unique set of parameters.
    params_unique = sorted(set(params))

    header = ["filepath", "function_name", "nloops", "time_taken_ms"] + params_unique

    # now use csvfile to convert dict into csv.
    with open(os.path.join(os.getcwd(), cche_file), "w", newline="") as csvfile:
        writer = csv.writer(
            csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        # write header.
        writer.writerow(header)
        # write each row.
        for file_path, items in writable_speedtest_cache.items():
            # convert file_path to relative
            file_path_rel = os.path.relpath(file_path)

            for func_name, parameters in items.items():
                # strip any [] brackets from the func name.
                func_name_stripped = func_name.split("[", 1)[0]

                # extract param__ arguments and map them to the correct location.
                _params = [None] * len(params_unique)
                # assign each parameter to to correct position within the unique parameter.
                for p in filter(lambda s: s.startswith("param__"), parameters):
                    _params[params_unique.index(p)] = parameters[p]

                writer.writerow(
                    [
                        file_path_rel,
                        func_name_stripped,
                        parameters["nloops"],
                        parameters["score"] * 1e3,
                    ]
                    + _params
                )
    return cche_file


def write_txt(writable_speedtest_cache: Dict[str, Any]) -> str:
    """Creates TXT log file."""
    cche_file = _get_cache_file_name("run", ".txt")

    with open(os.path.join(os.getcwd(), cche_file), "wt", encoding="utf-8") as txtfile:
        for file_path, items in writable_speedtest_cache.items():
            # convert file_path to relative
            file_path_rel = os.path.relpath(file_path)
            for func_name, parameters in items.items():
                txtfile.write(
                    "{}:{} | {} loops, {} / loop\n".format(
                        file_path_rel,
                        func_name,
                        parameters["nloops"],
                        stringify_time(parameters["score"]),
                    )
                )
    return cche_file


def read_toml(fname: str = "pyproject.toml", local_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Loads the ./pyproject.toml."""

    # attempt to import tomllib, and if not, raise a warning and return {}
    try:
        tomllib = importlib.import_module("tomllib")
    except ImportError:
        warnings.warn("""A `pyproject.toml` file was detected but unable to parse using `tomllib`"""
                      f""" due to requiring 'python>=3.11', your version is {sys.version.split()[0]}; consider upgrading.""", UserWarning)
        return {}

    if local_dir is None:
        local_dir = Path.cwd()
    path = local_dir / fname

    # if the file is present, open it and load the project.file.
    if os.path.isfile(path):
        with open(path, "rb") as tomlf:
            data = tomllib.load(tomlf)
        # if our tool is present...
        if "tool.speedtest" in data:
            return data["tool.speedtest"]
    return {}
