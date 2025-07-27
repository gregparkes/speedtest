"""
Example of a basic speedtest using the speedtest library.
This file is used to test the speedtest functionality in a simple manner.
It includes a fixture and two functions that perform list comprehensions.
This is a minimal example to demonstrate the speedtest capabilities.

@MIT license.
"""

import speedtest


@speedtest.fixture
def number():
    return 42


def speed_square_list_comp():
    _ = [x**2 for x in range(100000)]


def speed_square_list_comp2(number):
    # uses the fixture()
    _ = [(x * number) ** 2 for x in range(100000)]
