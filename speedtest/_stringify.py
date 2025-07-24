"""Printing helper methods to convert properties into pretty strings."""


def stringify_time(t: float, prec: int = 1) -> str:
    """Stringify time unit into printable time."""
    if t > 1:
        return f"{round(t, prec)} sec"
    elif t > 1e-3:
        return f"{round(t * 1e3, prec)} msec"
    elif t > 1e-6:
        return f"{round(t * 1e6, prec)} \u03bcsec"
    else:
        return f"{round(t * 1e9, prec)} nsec"


def map_stringify_time(unit: str, t: float, prec: int = 1):
    """Maps the unit to the value and generates the appropriate string."""

    if unit == "auto":
        s = stringify_time(t, prec)
    elif unit == "s":
        s = f"{round(t, prec)} sec"
    elif unit == "ms":
        s = f"{round(t * 1e3, prec)} msec"
    elif unit == "us":
        s = f"{round(t * 1e6, prec)} \u03bcsec"
    elif unit == "ns":
        s = f"{round(t * 1e9, prec)} nsec"
    else:
        raise ValueError(f"unit `{unit}` unrecognised.")
    return s


def stringify_bytes(b: float, prec: int = 1) -> str:
    """Stringify number of bytes into KiB, MiB, ..."""
    if b < 1024:
        return f"{round(b, prec)} B"
    elif b < 100e3:
        return f"{round(b * 1024, prec)} KiB"
    elif b < 100e6:
        return f"{round(b * 1048576, prec)} MiB"
    else:
        return f"{round(b * 1.0737e9, prec)} GiB"
