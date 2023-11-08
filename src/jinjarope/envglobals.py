from __future__ import annotations

from collections.abc import Mapping, Sequence
import datetime
import functools
import importlib

from importlib import metadata
import json
import logging
import os
import pathlib
import platform
import pprint
import sys
import tomllib
from typing import Any

from jinjarope import utils


logger = logging.getLogger(__name__)


version_info = dict(
    python_version=sys.version.split("(")[0].strip(),
    jinja_version=metadata.version("jinja2"),
    jinjarope_version=metadata.version("jinjarope"),
    system=platform.system(),
    architecture=platform.architecture(),
    python_implementation=platform.python_implementation(),
)


@functools.cache
def load_file_cached(path: str | os.PathLike) -> str:
    if "://" in str(path):
        return utils.fsspec_get(str(path))
    return pathlib.Path(path).read_text(encoding="utf-8")


def get_output_from_call(
    call: str | Sequence[str],
    cwd: str | os.PathLike | None,
) -> str | None:
    import subprocess

    if not isinstance(call, str):
        call = " ".join(call)
    try:
        return subprocess.run(
            call,
            stdout=subprocess.PIPE,
            text=True,
            shell=True,
            cwd=cwd,
        ).stdout
    except subprocess.CalledProcessError:
        logger.warning("Executing %s failed", call)
        return None


def format_js_map(mapping: dict | str, indent: int = 4) -> str:
    """Return JS map str for given dictionary.

    Arguments:
        mapping: Dictionary to dump
        indent: The amount of indentation for the key-value pairs
    """
    dct = json.loads(mapping) if isinstance(mapping, str) else mapping
    rows = []
    indent_str = " " * indent
    for k, v in dct.items():
        match v:
            case bool():
                rows.append(f"{indent_str}{k}: {str(v).lower()},")
            case dict():
                rows.append(f"{indent_str}{k}: {format_js_map(v)},")
            case None:
                rows.append(f"{indent_str}{k}: null,")
            case _:
                rows.append(f"{indent_str}{k}: {v!r},")
    row_str = "\n" + "\n".join(rows) + "\n"
    return f"{{{row_str}}}"


def format_css_rule(dct: Mapping) -> str:
    """Format a nested dictionary as CSS rule.

    Mapping must be of shape {".a": {"b": "c"}}

    Arguments:
        dct: The mapping to convert to CSS text
    """
    data: dict[str, list] = {}

    def _parse(obj, selector: str = ""):
        for key, value in obj.items():
            if hasattr(value, "items"):
                rule = selector + " " + key
                data[rule] = []
                _parse(value, rule)

            else:
                prop = data[selector]
                prop.append(f"\t{key}: {value};\n")

    _parse(dct)
    string = ""
    for key, value in sorted(data.items()):
        if data[key]:
            string += key[1:] + " {\n" + "".join(value) + "}\n\n"
    return string


def add(text, prefix: str = "", suffix: str = ""):
    if not text:
        return ""
    return f"{prefix}{text}{suffix}"


def regex_replace(
    value: str = "",
    pattern: str = "",
    replacement: str = "",
    ignorecase: bool = False,
    multiline: bool = False,
    count: int = 0,
):
    """Perform a `re.sub` returning a string.

    Arguments:
        value: The value to search-replace.
        pattern: The regex pattern to use
        replacement: The replacement pattern to use
        ignorecase: Whether to ignore casing
        multiline: Whether to do a multiline regex search
        count: Amount of maximum substitutes.
    """
    import re

    flags = 0
    if ignorecase:
        flags |= re.I
    if multiline:
        flags |= re.M
    pat = re.compile(pattern, flags=flags)
    output, _subs = pat.subn(replacement, value, count=count)
    return output


def ternary(value: Any, true_val: Any, false_val: Any, none_val: Any = None):
    """Value ? true_val : false_val.

    Arguments:
        value: The value to check.
        true_val: The value to return if given value is true-ish
        false_val: The value to return if given value is false-ish
        none_val: Optional value to return if given value is None
    """
    if value is None and none_val is not None:
        return none_val
    if bool(value):
        return true_val
    return false_val


ENV_GLOBALS = {
    "now": datetime.datetime.now,
    "importlib": importlib,
    "environment": version_info,
}
ENV_FILTERS = {
    "pformat": pprint.pformat,
    "repr": repr,
    "rstrip": str.rstrip,
    "lstrip": str.lstrip,
    "removesuffix": str.removesuffix,
    "removeprefix": str.removeprefix,
    "regex_replace": regex_replace,
    "add": add,
    "ternary": ternary,
    "issubclass": issubclass,
    "isinstance": isinstance,
    "import_module": importlib.import_module,
    "hasattr": hasattr,
    "partial": functools.partial,
    "dump_json": json.dumps,
    "load_json": json.loads,
    "load_toml": tomllib.loads,
    "load_file": load_file_cached,
    "path_join": os.path.join,
    "format_js_map": format_js_map,
    "format_css_rule": format_css_rule,
    "check_output": get_output_from_call,
    "getenv": os.getenv,
}


if __name__ == "__main__":
    a = format_js_map({"test": "abc"})
    print(a)
