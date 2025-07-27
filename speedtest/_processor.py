"""Processes Python files and generates speedtest results."""

# from collections.abc import Callable
import os
import platform
import sys
import importlib
import importlib.metadata
import itertools as it
import glob
import inspect
from pathlib import Path
from functools import partial
import timeit
from multiprocessing import Pool, cpu_count
from typing import List, Callable

from speedtest._kwargs import Kwargs
from speedtest._speedtree import parse_python_to_tree
from speedtest._log import log_output, optional_rich_status
from speedtest._stringify import stringify_time, map_stringify_time
from speedtest._ioops import (
    read_cache,
    write_cache,
    write_csv,
    write_txt,
)


def _is_valid_python_file(path: str) -> bool:
    """Tests whether the provided path is a valid Python file."""
    return (
        os.path.isfile(path)
        and os.path.basename(path).lower().startswith("speed")
        and os.path.splitext(path)[-1].lower() == ".py"
    )


@optional_rich_status("Discovering source files...")
def _discover_source_files(srcs: List[str]) -> List[str]:
    """Discover all valid Python source files.

    Parameters
    ----------
    srcs : List[str]
        List of source file paths to discover valid Python files from.

    Returns
    -------
    List[str]
        List of valid Python source file paths.
    """

    all_parsable_files: List[str] = []

    # loop over the file and folder sources and extract all valid Python files.
    for file_or_dir in srcs:
        # map the directory / file to the current location.
        file_or_dir_local = os.path.expanduser(os.path.join(os.getcwd(), file_or_dir))

        # if the file / folder doesn't exist - skip
        if not os.path.exists(file_or_dir_local):
            continue

        # if it points to a valid Python file, add to the list.
        if _is_valid_python_file(file_or_dir_local):
            all_parsable_files.append(file_or_dir_local)

        # points to a directory structure - use glob to scan the Python files
        # in the sub-folders of the directory.
        elif os.path.isdir(file_or_dir_local):
            valid_files = [
                f
                for f in glob.glob(
                    os.path.join(file_or_dir_local, "**/*.py"), recursive=True
                )
                if _is_valid_python_file(f)
            ]
            all_parsable_files.extend(valid_files)

    # remove any duplicates.
    return list(set(all_parsable_files))


def _process_source_file(src: str, kwargs: Kwargs, cache_data):
    """
    Processes a given source file and times all detected methods within.

    Parameters
    ----------
    src : str
        Path to the source Python file to process.
    kwargs : Kwargs
        Command line keyword arguments controlling behavior such as verbosity,
        cache usage, and output formatting.
    cache_data : dict
        Cacheable data containing previously computed timing results.

    Returns
    -------
    writable_speedtest_cache : dict
        Writable items to store in cache files, mapping source files and method
        signatures to timing properties.
    """

    # -------------------------------------------------------------
    #   Parse the source code into an AST tree
    # -------------------------------------------------------------
    children = parse_python_to_tree(Path(src))

    log = partial(log_output, kwargs=kwargs)

    # load the Python script as a module first.
    # firstly, add the Python script into the sys.path field.
    script_name = os.path.splitext(os.path.basename(src))[0]
    rel_path_to_script = os.path.relpath(src, os.getcwd())
    dir_shift_to_script = os.path.dirname(rel_path_to_script)

    # -------------------------------------------------------------
    #   Include the current script on the system PATH
    # -------------------------------------------------------------
    if dir_shift_to_script != "" and dir_shift_to_script not in sys.path:
        # insert path into sys.path
        sys.path.append(dir_shift_to_script)

    # import module
    module_ = importlib.import_module(script_name)

    # -------------------------------------------------------------
    #   Configures the spacing of the {} loops, text on the
    #       print out
    # -------------------------------------------------------------
    nloops_pad_width = 10  # default
    if cache_data:
        # collect 'nloops' property across the cache.
        loopies = list(
            it.chain.from_iterable(
                [
                    [cache_data[y][x]["nloops"] for x in cache_data[y]]
                    for y in cache_data
                ]
            )
        )
        # the length of the integer + 6 is set to the new pad width (always correct.)
        nloops_pad_width = 6 + max(map(len, map(str, loopies)))

    writable_speedtest_cache = {}
    prints = []
    # -------------------------------------------------------------
    #       Loop over every function name that was detected
    #       and time it.
    # -------------------------------------------------------------
    for i, method in enumerate(children.methods):
        # get function method as an object.
        script_func = getattr(module_, method.name)

        #   check if script_func is a generator - this indicates that its part of a
        #   parametrize() call.
        if inspect.isgenerator(script_func):
            # loop over the functions.
            funcs = [f for f in script_func]
        else:
            funcs = [script_func]

        # if the function has any fixtures, run the fixtures first and collect the arguments to attach to the function.
        if method.fixtures:
            results = [getattr(module_, fix)() for fix in method.fixtures]
            # map keyword arguments
            fixture_kws = {fix: data for fix, data in zip(method.fixtures, results)}
        else:
            fixture_kws = {}

        # loop over the functions and apply them.
        for script in funcs:
            # use inspect to extract any parameters, and add them to the print statement.
            sig = inspect.getfullargspec(script)
            if sig.kwonlydefaults:
                printable_parameters = (
                    "{"
                    + ",".join(
                        ["'{}'={}".format(k, v) for k, v in sig.kwonlydefaults.items()]
                    )
                    + "}"
                )
            else:
                printable_parameters = ""

            # if any fixtures are defined, attach them to script using partial(...)
            if len(fixture_kws) > 0:
                script = partial(script, **fixture_kws)

            timer = timeit.Timer(script)

            # check if the cache contains the function specified.
            if (not kwargs.ignore_cache or not kwargs.no_cache) and (
                src in cache_data
                and (method.name + printable_parameters) in cache_data[src]
            ):
                # extract nloops from cache, skip step.
                properties = cache_data[src][method.name + printable_parameters]
            else:
                # compute using autorange.
                try:
                    nloops, best_score = timer.autorange()
                    # append data to the cache.
                    properties = {"nloops": nloops, "score": best_score / nloops}
                    if sig.kwonlydefaults:
                        properties.update(
                            {"param__" + k: v for k, v in sig.kwonlydefaults.items()}
                        )
                except Exception:
                    properties = {"nloops": 5, "score": 0}

            # using best n-loops, repeat rep times.
            # on recommendation of the timer.repeat docstrings - we take the min() of the scores as a lower-bound for best-case-scenario of speed.
            # wrap the function call in try-catch.
            try:
                if not kwargs.parallel:
                    timer_func = optional_rich_status(
                        f"Processing '{script_name}.py' ({i+1}/{len(children.methods)})..."
                    )(timer.repeat)
                else:
                    timer_func = timer.repeat

                # run the timer and collect the scores.
                scores = timer_func(repeat=kwargs.nreps, number=properties["nloops"])
                # scores = timer.repeat(repeat=kwargs.nreps, number=properties["nloops"])
                best_time_loop = min(scores) / properties["nloops"]
                # update the best score to store in the cache.
                properties["score"] = best_time_loop

                rhs_print = "{} loop{}".format(
                    properties["nloops"], "s" if properties["nloops"] != 1 else ""
                ).ljust(nloops_pad_width) + ", {} per loop".format(
                    stringify_time(properties["score"])
                    if kwargs.unit == "auto"
                    else map_stringify_time(kwargs.unit, properties["score"])
                )

            except Exception as e:  # pragma: no cover
                # print the exception.
                if kwargs.verbose < 1:
                    rhs_print = f"FAILED ({e.__class__.__name__})"
                else:
                    rhs_print = f"FAILED ({e.__class__.__name__}): {e}"

            if src in writable_speedtest_cache:
                writable_speedtest_cache[src][
                    method.name + printable_parameters
                ] = properties
            else:
                writable_speedtest_cache[src] = {
                    method.name + printable_parameters: properties
                }

            # calculate the average time per loop
            lhs_print = (
                f"{rel_path_to_script}:{method.name}{printable_parameters} ".ljust(
                    kwargs.print_pad_width, "-"
                )
            )

            print_str = f"{lhs_print} {rhs_print}"

            if not kwargs.parallel:
                log(print_str)

            prints.append(print_str)

    return writable_speedtest_cache, prints


def run_session(kwargs: Kwargs, logger: Callable[[str], None]) -> None:
    """Launches a speedtest session.

    Args:
        sources (list[str]): List of Python file sources.
        kwargs (Kwargs): keyword arguments.
        logger (Callable[[str], None]): Logging function.
    """

    # display version and initial command prompt to user.
    curr_version = importlib.metadata.version("speedtest")
    print(
        "================================================= test session starts ================================================="
    )
    logger(
        "Platform {} -- Python {}.{}.{}, speedtest {}".format(
            platform.system(),
            sys.version_info.major,
            sys.version_info.minor,
            sys.version_info.micro,
            curr_version,
        )
    )

    # --------------------------------------------------------------------------------------------
    #   Collect all Python files.
    # --------------------------------------------------------------------------------------------
    parsable_files = _discover_source_files(kwargs.file_or_dir)

    logger(
        "collected {} file{}, best of {}:\n".format(
            len(parsable_files), "s" if len(parsable_files) != 1 else "", kwargs.nreps
        )
    )

    # --------------------------------------------------------------------------------------------
    #   Scan each Python file and find all speed_* methods within the script.
    # --------------------------------------------------------------------------------------------
    writable_speedtest_cache = {}
    read_speedtest_cache = read_cache() if not kwargs.no_cache else {}

    # in sequential execution, we process each file one at a time.
    if not kwargs.parallel or len(parsable_files) <= 1:
        # execute sequentially.
        for src in sorted(parsable_files):
            cache_, _ = _process_source_file(src, kwargs, read_speedtest_cache)
            writable_speedtest_cache.update(cache_)

    else:
        # determine number of cores.
        num_processes = max(min(len(parsable_files), cpu_count() - 1), 1)
        mp_args = [
            (src, kwargs, read_speedtest_cache) for src in sorted(parsable_files)
        ]

        # execute and block in parallel.
        with Pool(processes=num_processes) as pool:
            results = pool.starmap(_process_source_file, mp_args)

        # combine results into a single JSON.
        for cache_, stdout in results:
            for item in stdout:
                logger(item)
            writable_speedtest_cache.update(cache_)

    # --------------------------------------------------------------------------------------------
    #   Write cache.json / any other file outputs as a result of the speedtest run.
    # --------------------------------------------------------------------------------------------
    if not kwargs.no_cache and len(writable_speedtest_cache) > 0:
        write_cache(writable_speedtest_cache)

    if kwargs.tocsv:
        # creates a CSV file from the cache.json content.
        csvfile_name = write_csv(writable_speedtest_cache)
        logger(f"Success! Saved CSV output to '{csvfile_name}'")

    if kwargs.totxt:
        # creates .TXT log file
        txtfile_name = write_txt(writable_speedtest_cache)
        logger(f"Success! Saved TXT output to '{txtfile_name}'")
