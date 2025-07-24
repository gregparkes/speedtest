from dataclasses import dataclass
from typing import List

@dataclass
class Kwargs:
    """Command line keyword arguments."""

    file_or_dir: List[str]
    unit: str = "auto"
    no_cache: bool = False
    parallel: bool = False
    nreps: int = 3
    tocsv: bool = False
    totxt: bool = False
    ignore_cache: bool = False
    print_pad_width: int = 100
    quiet: bool = False
    verbose: int = 0
    rich_installed: bool = False
