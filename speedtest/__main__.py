"""__main__ interface."""

import os
import argparse
import importlib
import importlib.metadata
from typing import Any
from functools import partial

# local import
from speedtest._kwargs import Kwargs
from speedtest._ioops import (
    read_toml,
    read_ini,
)
from speedtest._log import log_output
from speedtest._processor import run_session


def cliargs_argparser() -> dict[str, Any]:  # pragma: no cover
    """Generates command line arguments using the default Python argparse library."""

    parser = argparse.ArgumentParser(
        description="Testing the performance of your code in a PyTest-style format."
    )
    parser.add_argument(
        "file_or_dir", nargs="*", help="Path to file or directory of Python files."
    )
    parser.add_argument(
        "--unit",
        choices=("s", "ms", "us", "ns", "auto"),
        default="auto",
        help="Forces all time units to share the same unit. (default='auto')",
    )
    parser.add_argument(
        "--parallel", action="store_true", help="Computes using multiprocessing."
    )
    parser.add_argument(
        "--nreps",
        type=int,
        default=3,
        help="Number of repetitions per test. (default=3)",
    )
    parser.add_argument("--tocsv", action="store_true", help="Generates a CSV table.")
    parser.add_argument("--totxt", action="store_true", help="Generates a text log.")
    parser.add_argument(
        "--no-cache", action="store_true", help="No read/write caching."
    )
    parser.add_argument(
        "--ignore-cache", action="store_true", help="Ignores .speedtest_cache if set."
    )
    parser.add_argument(
        "--print-pad-width",
        type=int,
        default=100,
        help="Pad width when reporting speeds. (default=100)",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppresses all printing."
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Verbosity level."
    )

    args = parser.parse_args()
    args_dict = vars(args)

    return args_dict


def main(args_dict):
    #######################################################
    #   Main entry point
    #######################################################

    kwargs_dict = {}

    # if dotenv is installed, and .env is detected, provide arguments.
    try:
        module_ = importlib.import_module("dotenv")
        # load arguments using dotenv
        dotenv_dict = module_.dotenv_values(".env")
        # remove SPEEDTEST_ from dict keys, set to lower.
        dotenv_dict = {
            k[10:].lower(): v
            for k, v in dotenv_dict.items()
            if k.startswith("SPEEDTEST_")
        }

    except ImportError:
        dotenv_dict = {}

    # check whether rich is installed, and if so set it in kwargs
    try:  # pragma: no cover
        importlib.import_module("rich")
        kwargs_dict["rich_installed"] = True
    except ImportError:  # pragma: no cover
        kwargs_dict["rich_installed"] = False

    ##############################################################################################
    #   Collapse command-line and TOML arguments into a cohesive keyword-parameter set.
    ##############################################################################################

    # Set default properties.
    if len(args_dict["file_or_dir"]) == 0:
        args_dict["file_or_dir"] = ["."]

    # check whether speedtest.ini exists, and if so load it.
    if os.path.isfile(os.path.join(os.getcwd(), "speedtest.ini")):
        kwargs_dict.update(read_ini())

    # load pyproject.toml and override from CMD.
    if os.path.isfile(os.path.join(os.getcwd(), "pyproject.toml")):
        kwargs_dict.update(read_toml("pyproject.toml"))

    kwargs_dict.update(dotenv_dict)
    kwargs_dict.update(args_dict)
    kwargs = Kwargs(**kwargs_dict)

    log = partial(log_output, kwargs=kwargs)

    # call the session.
    run_session(kwargs, log)


def cli_interface():  # pragma: no cover
    args = cliargs_argparser()
    # redundant, supports `python -m speedtest` call interface
    main(args)


if __name__ == "__main__":  # pragma: no cover
    cli_interface()
