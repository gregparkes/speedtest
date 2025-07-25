"""Tests tree generation on different Python inputs."""

import textwrap
from speedtest._speedtree import parse_python_to_tree
import pytest


def test_basic():
    inputs = textwrap.dedent("""\n
    def speed_basic():
        _ = [x * 2 for x in range(1000)]

    """)

    r = parse_python_to_tree(str(inputs))

    assert len(r.methods) == 1
    assert r.methods[0].name == "speed_basic"
    assert r.methods[0].fixtures == []


@pytest.mark.parametrize(
    "inputs",
    [
        textwrap.dedent("""\n
    import speedtest
    @speedtest.mark
    def normal_basic():
        _ = [x * 2 for x in range(1000)]

    """),
        textwrap.dedent("""\n
    from speedtest import mark
    @mark
    def normal_basic():
        _ = [x * 2 for x in range(1000)]

    """),
    ],
)
def test_mark(inputs):
    r = parse_python_to_tree(str(inputs))
    assert len(r.methods) == 1
    assert r.methods[0].name == "normal_basic"
    assert r.methods[0].fixtures == []


def test_multi():
    inputs = textwrap.dedent("""\n
    def speed_basic():
        _ = [x * 2 for x in range(1000)]

    def speed_basic2():
        return 42
    """)

    true_methods = ["speed_basic", "speed_basic2"]

    r = parse_python_to_tree(str(inputs))
    assert len(r.methods) == 2

    for truth, func in zip(true_methods, r.methods):
        assert truth == func.name


def test_fixture():
    inputs = textwrap.dedent("""\n
    import speedtest
    @speedtest.fixture
    def result():
        return 42

    def speed_basic(result):
        return result + 1
    """)

    r = parse_python_to_tree(str(inputs))
    assert len(r.methods) == 1
    assert r.methods[0].name == "speed_basic"
    assert r.methods[0].fixtures[0] == "result"
