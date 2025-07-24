"""Provides a parametrize() decorator for running multiple speed-tests."""

from typing import Any, Callable, Union, Tuple, List
from functools import partial


def parametrize(argnames: str, argvalues: List[Union[Any, Tuple[Any, ...]]]):
    """Wraps a speed_ function with a parameter."""

    # split argnames into multiple if we can.
    arg_name_list = [s.strip() for s in argnames.split(",")]

    def decorator(func: Callable):
        # define our parameters, wrap with partial and return?
        for args in argvalues:
            if isinstance(args, (list, tuple)):
                params = dict(zip(arg_name_list, args))
            else:
                params = {arg_name_list[0]: args}

            # return the function wrapped in partial params.
            yield partial(func, **params)

    return decorator


def fixture(func: Callable):
    """@speedtest.fixture. Declares method as a fixture for use in speedtesting.

    Does nothing apart from inform AST."""
    return func  # pragma: no cover


def mark(func: Callable):
    """@speedtest.mark. Marks the method for speedtesting even if it isn't called speed_*.

    Does nothing apart from inform AST."""
    return func  # pragma: no cover
