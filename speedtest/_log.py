"""Handles printing and logging."""

import importlib
from functools import wraps

from speedtest._kwargs import Kwargs


def log_output(content: str, kwargs: Kwargs) -> None:
    """Logs content if appropriate."""

    if not kwargs.quiet:
        try:
            importlib.import_module("rich")
            from rich.console import Console

            console = Console()
            console.print(content)

        except ImportError:
            print(content)


def optional_rich_status(msg: str | None = None):
    """Wrapper function to use rich status."""

    if msg is None:
        msg = "Processing..."

    def decorator(func):
        """Decorator to wrap the function."""
        try:
            importlib.import_module("rich")
            from rich.status import Status

            @wraps(func)
            def wrapped(*args, **kwargs):
                with Status(msg) as status:
                    return func(*args, **kwargs)

            return wrapped

        except ImportError:
            return func

    return decorator
