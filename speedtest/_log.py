"""Handles printing and logging."""

import importlib

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
