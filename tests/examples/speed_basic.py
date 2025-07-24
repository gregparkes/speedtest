"""Example 1."""

import speedtest


@speedtest.fixture
def number():
    return 42


def speed_square_list_comp():
    _ = [x**2 for x in range(100000)]


def speed_square_list_comp2(number):
    # uses the fixture()
    _ = [(x * number) ** 2 for x in range(100000)]
