"""Tests running a session against this Pytest repo."""

import os
import shutil
from pathlib import Path
from speedtest._kwargs import Kwargs
from speedtest._processor import run_session


def test_run_session_basic():
    # session with no files.
    run_session(Kwargs(file_or_dir=["."], no_cache=True), print)


def test_run_session_examples():
    path = str(Path(__file__).parent / "./examples/speed_basic.py")
    run_session(
        Kwargs(file_or_dir=[path], ignore_cache=True, totxt=True, tocsv=True), print
    )
    # clean up speedtest-cache, and output files.
    shutil.rmtree(Path.cwd() / ".speedtest_cache")
    os.remove(Path.cwd() / "run.csv")
    os.remove(Path.cwd() / "run.txt")


def test_run_session_examples_parallel():
    path = str(Path(__file__).parent / "./examples/speed_basic.py")
    run_session(Kwargs(file_or_dir=[path], no_cache=True, parallel=True), print)
