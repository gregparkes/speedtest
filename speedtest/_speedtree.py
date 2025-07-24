"""Uses AST to analyse a speedtest Python file."""

import ast
import pathlib
from dataclasses import dataclass
from typing import Union, List


@dataclass
class SpMethod:
    """A speed-based method with its associated attributes."""

    name: str
    fixtures: List[str]


@dataclass
class SpeedTree:
    """Defines a parsed Python object into its defined speed methods, fixtures and other properties."""

    methods: List[SpMethod]


def parse_python_to_tree(src: Union[str, pathlib.Path]) -> SpeedTree:
    """Parse a Python file into associated runnable methods with fixtures."""

    if isinstance(src, pathlib.Path):
        # load the python file into memory.
        with open(src, "rt", encoding="utf-8") as pyfile:
            src_code = pyfile.read()
    else:
        src_code = src

    ########################################
    #   Parse the source code into AST
    ########################################
    tree = ast.parse(src_code)

    speed_fs = []
    fixture_fs = []

    decorator_rel_import = {"mark": "unk", "parametrize": "unk", "fixture": "unk"}
    # speedtest_direct_import = False

    # confirm whether 'speedtest' is imported.
    for node in tree.body:
        # if isinstance(node, ast.Import) and any(
        #     n.name == "speedtest" for n in node.names
        # ):
        #     speedtest_direct_import = True
        if isinstance(node, ast.ImportFrom) and node.module == "speedtest":
            # loop through aliases and see if 'speedtest.mark' exist
            for alias in node.names:
                if alias.name in ("mark", "parametrize", "fixture"):
                    decorator_rel_import[alias.name] = "rel"

    # loop through the nodes and identify any speed / fixture functions.
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith("speed_"):
                speed_fs.append(node.name)

            # else check if its a fixture
            else:
                for dec in node.decorator_list:
                    # check for global import of fixture
                    # e.g import speedtest; @speedtest.fixture
                    if (
                        isinstance(dec, ast.Attribute)
                        and isinstance(dec.value, ast.Name)
                        and dec.value.id == "speedtest"
                        and dec.attr == "fixture"
                    ):
                        fixture_fs.append(node.name)
                    # check for relative import of fixture
                    # e.g from speedtest import fixture; @fixture
                    elif (
                        decorator_rel_import["fixture"] == "rel"
                        and isinstance(dec, ast.Name)
                        and dec.id == "fixture"
                    ):
                        fixture_fs.append(node.name)
                    # check for global import of mark
                    # e.g import speedtest; @speedtest.mark
                    elif (
                        isinstance(dec, ast.Attribute)
                        and isinstance(dec.value, ast.Name)
                        and dec.value.id == "speedtest"
                        and dec.attr == "mark"
                    ):
                        speed_fs.append(node.name)
                    # check for relative import of mark
                    # e.g from speedtest import mark; @mark
                    elif (
                        decorator_rel_import["mark"] == "rel"
                        and isinstance(dec, ast.Name)
                        and dec.id == "mark"
                    ):
                        speed_fs.append(node.name)

    # eliminate duplicates
    speed_fs = list(set(speed_fs))
    fixture_fs = list(set(fixture_fs))

    sp_methods = []

    # loop back again through the speed methods, and associate properties to each.
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in speed_fs:
            node_fixtures = []
            # generate a speed tree.
            for a in node.args.args:
                if isinstance(a, ast.arg) and a.arg in fixture_fs:
                    node_fixtures.append(a.arg)

            sp_methods.append(SpMethod(name=node.name, fixtures=node_fixtures))

    return SpeedTree(methods=sp_methods)
