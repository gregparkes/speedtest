"""Test reading of cache files."""

import json
import os
import pytest

from speedtest._ioops import read_cache, read_ini, read_toml


@pytest.fixture
def cache_file(tmpdir) -> str:
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
    outfile = os.path.join(tmpdir, "speedtest.ini")
    with open(outfile, "wt") as fid:
        fid.write("[speedtest]\n")
        fid.write("unit = ms\n")
        fid.write("no_cache = true\n")
        fid.write("print_pad_width = 80\n")
    return outfile


@pytest.fixture
def toml_file(tmpdir) -> str:
    outfile = os.path.join(tmpdir, "pyproject.toml")
    with open(outfile, "wt") as fid:
        fid.write("\n[tool.speedtest]\n")
        fid.write('unit = "ms"\n')
    return tmpdir


def test_read_cache(cache_file):
    read_cache(cache_dir=os.path.join(cache_file, ".speedtest_cache"))


def test_read_ini(ini_file):
    read_ini(ini_file)


def test_read_toml(toml_file):
    read_toml(local_dir=toml_file)
