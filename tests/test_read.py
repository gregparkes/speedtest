"""Test reading of cache files."""

import json
import os
from pathlib import Path
import tomllib
import pytest

from speedtest._ioops import read_cache, read_ini, read_toml


@pytest.fixture
def cache_file(tmpdir) -> str:
    """Generates a cache file."""
    out_dir = os.path.join(tmpdir, ".speedtest_cache")
    os.mkdir(out_dir)

    out_file = os.path.join(out_dir, "cache.json")
    with open(out_file, "wt") as fid:
        json.dump(
            {
                os.path.abspath(os.path.join(tmpdir, "speed_test.py")): {
                    "speed_func": {"nloops": 10, "score": 0.5}
                }
            },
            fid,
        )

    return tmpdir


@pytest.fixture
def ini_file(tmpdir) -> str:
    """Generates an ini file."""
    outfile = os.path.join(tmpdir, "speedtest.ini")
    with open(outfile, "wt") as fid:
        fid.write("[speedtest]\n")
        fid.write("unit = ms\n")
        fid.write("no_cache = true\n")
        fid.write("print_pad_width = 80\n")
    return outfile


@pytest.fixture
def toml_file(tmpdir) -> str:
    """Generates a TOML file."""
    outfile = os.path.join(tmpdir, "pyproject.toml")
    with open(outfile, "wt", encoding="utf-8") as fid:
        fid.write("\n[tool.speedtest]\n")
        fid.write('unit = "ms"\n')
    return tmpdir


def test_read_cache(cache_file):
    """Read a cache file."""
    read_cache(cache_dir=os.path.join(cache_file, ".speedtest_cache"))


def test_read_ini(ini_file):
    """Tests reading an ini file."""
    ini_data = read_ini(ini_file)
    assert ini_data == {
        "unit": "ms",
        "no_cache": True,
        "print_pad_width": 80,
    }


def test_read_ini_no_file():
    """Tests reading an ini file that does not exist."""
    with pytest.warns(
        UserWarning, match="No `speedtest` section found in the ini file."
    ):
        no_ini_data = read_ini("fake.ini")
    assert no_ini_data == {}


def test_read_toml(toml_file):
    """Reads in a TOML file."""
    toml_data = read_toml(local_dir=Path(toml_file))
    assert toml_data == {
        "unit": "ms",
    }


def test_read_toml_no_file():
    """Tests reading a TOML file that does not exist."""
    with pytest.warns(
        UserWarning,
        match="No `pyproject.toml` file found or it does not contain the 'tool.speedtest' section.",
    ):
        no_toml_data = read_toml(local_dir=Path("fake_dir"))
    assert no_toml_data == {}
