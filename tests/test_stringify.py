import pytest
from speedtest._stringify import stringify_time, stringify_bytes, map_stringify_time


@pytest.mark.parametrize("value", [2.0, 1e-2, 1e-5, 1e-8])
def test_stringify_time(value):
    stringify_time(value)


@pytest.mark.parametrize("value", [1e3, 1e4, 1e6, 1e9, 1e12])
def test_stringify_bytes(value):
    stringify_bytes(value)


@pytest.mark.parametrize("unit", ["auto", "s", "ms", "us", "ns"])
def test_stringify_map_time(unit):
    map_stringify_time(unit, 1.0)


def test_exception_no_unit():
    with pytest.raises(ValueError):
        map_stringify_time("Not_a_unit", 1.0)
