"""
Example of a basic speedtest using the speedtest library.
This file is used to test the speedtest functionality by comparing
    raw Python and NumPy implementations.
It includes two functions that perform list comprehensions and a for loop.
This is a minimal example to demonstrate the speedtest capabilities.

@MIT license.
"""

from speedtest import fixture


@fixture
def number():
    """Fixture that returns a number."""
    return 100000


def speed_square_for_loop(number):
    """Performs a for loop to square numbers."""
    _ = []
    for x in range(number):
        _ += [x**2]


def speed_square_list_comp(number):
    """Performs a list comprehension to square numbers."""
    _ = [x**2 for x in range(number)]


def speed_square_numpy(number):
    """Performs a numpy operation to square numbers."""
    import numpy as np

    _ = np.arange(number) ** 2
