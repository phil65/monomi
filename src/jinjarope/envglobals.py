from __future__ import annotations

from collections.abc import Sequence
import configparser
import datetime
import functools
import importlib

from importlib import metadata
import io
import itertools
import json
import logging
import operator
import os
import pathlib
import platform
import pprint
import sys
import tomllib
from typing import Any, Literal

from jinjarope import envtests, htmlfilters, iterfilters, mdfilters, regexfilters, utils


logger = logging.getLogger(__name__)


version_info = dict(
    python_version=sys.version.split("(")[0].strip(),
    jinja_version=metadata.version("jinja2"),
    jinjarope_version=metadata.version("jinjarope"),
    system=platform.system(),
    architecture=platform.architecture(),
    python_implementation=platform.python_implementation(),
)


def serialize(data: Any, mode: Literal["yaml", "json", "ini", "toml"] | None) -> str:  # type: ignore[return]
    """Serialize given json-like object to given format.

    Arguments:
        data: The data to serialize
        mode: The serialization mode
    """
    match mode:
        case None | "yaml":
            import yaml

            return yaml.dump(data)
        case "json":
            return json.dumps(data, indent=4)
        case "ini":
            config = configparser.ConfigParser()
            config.read_dict(data)
            file = io.StringIO()
            with file as fp:
                config.write(fp)
                return file.getvalue()
        case "toml" if isinstance(data, dict):
            import tomli_w

            return tomli_w.dumps(data)
        case _:
            raise TypeError(mode)


@functools.cache
def load_file_cached(path: str | os.PathLike) -> str:
    """Return the str-content of file at given path.

    Arguments:
        path: The path to get str content from
    """
    if "://" in str(path):
        return utils.fsspec_get(str(path))
    return pathlib.Path(path).read_text(encoding="utf-8")


def get_output_from_call(
    call: str | Sequence[str],
    cwd: str | os.PathLike | None,
) -> str | None:
    """Execute a system call and return its output as a string.

    Arguments:
        call: The system call to make
        cwd: The working directory for the call
    """
    import subprocess

    if not isinstance(call, str):
        call = " ".join(call)
    try:
        pipe = subprocess.PIPE
        return subprocess.run(call, stdout=pipe, text=True, shell=True, cwd=cwd).stdout
    except subprocess.CalledProcessError:
        logger.warning("Executing %s failed", call)
        return None


def add(text, prefix: str = "", suffix: str = ""):
    if not text:
        return ""
    return f"{prefix}{text}{suffix}"


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


def resolve(name: str, module: str | None = None):
    """Resolve ``name`` to a Python object via imports / attribute lookups.

    If ``module`` is None, ``name`` must be "absolute" (no leading dots).

    If ``module`` is not None, and ``name`` is "relative" (has leading dots),
    the object will be found by navigating relative to ``module``.

    Returns the object, if found.  If not, propagates the error.
    """
    names = name.split(".")
    if not names[0]:
        if module is None:
            msg = "relative name without base module"
            raise ValueError(msg)
        modules = module.split(".")
        names.pop(0)
        while not name[0]:
            modules.pop()
            names.pop(0)
        names = modules + names

    used = names.pop(0)
    found = importlib.import_module(used)
    for n in names:
        used += "." + n
        try:
            found = getattr(found, n)
        except AttributeError:
            importlib.import_module(used)
            found = getattr(found, n)

    return found


def is_instance(obj: object, typ: str | type) -> bool:
    kls = resolve(typ) if isinstance(typ, str) else typ
    if not isinstance(kls, type):
        raise TypeError(kls)
    return isinstance(obj, kls)


def is_subclass(obj: type, typ: str | type) -> bool:
    kls = resolve(typ) if isinstance(typ, str) else typ
    if not isinstance(kls, type):
        raise TypeError(kls)
    return issubclass(obj, kls)


ENV_GLOBALS = {
    "zip": zip,
    "now": datetime.datetime.now,
    "utcnow": datetime.datetime.utcnow,
    "importlib": importlib,
    "environment": version_info,
}
ENV_FILTERS = {
    # Format filters
    "repr": repr,
    "pformat": pprint.pformat,
    "format_code": utils.format_code,
    # Markdown filters
    "md_link": mdfilters.md_link,
    "md_escape": mdfilters.md_escape,
    "md_style": mdfilters.md_style,
    "extract_header_section": mdfilters.extract_header_section,
    # HTML filters
    "html_link": htmlfilters.html_link,
    "wrap_in_elem": htmlfilters.wrap_in_elem,
    "format_js_map": htmlfilters.format_js_map,
    "format_css_rule": htmlfilters.format_css_rule,
    "svg_to_data_uri": htmlfilters.svg_to_data_uri,
    "clean_svg": htmlfilters.clean_svg,
    # Iter filters
    "batched": iterfilters.batched,
    "reduce_list": iterfilters.reduce_list,
    "flatten_dict": iterfilters.flatten_dict,
    "pairwise": itertools.pairwise,
    "zip": zip,
    "any": iterfilters.do_any,
    # Text modification filters
    "rstrip": str.rstrip,
    "lstrip": str.lstrip,
    "removesuffix": str.removesuffix,
    "removeprefix": str.removeprefix,
    # Regex filters
    "re_replace": regexfilters.re_replace,
    "re_findall": regexfilters.re_findall,
    "re_search": regexfilters.re_search,
    "re_escape": regexfilters.re_escape,
    # serialization filters
    "dump_json": json.dumps,
    "load_json": json.loads,
    "load_toml": tomllib.loads,
    "serialize": serialize,
    # misc
    "add": add,
    "ternary": ternary,
    "issubclass": is_subclass,
    "isinstance": is_instance,
    "import_module": importlib.import_module,
    "hasattr": hasattr,
    "partial": functools.partial,
    "load_file": load_file_cached,
    "path_join": os.path.join,
    "check_output": get_output_from_call,
    "getenv": os.getenv,
}


ENV_TESTS = {
    "is_number": envtests.is_number,
    "list": envtests._is_list,
    "set": envtests._is_set,
    "tuple": envtests._is_tuple,
    "dict": envtests._is_dict,
    "datetime": envtests._is_datetime,
    "string_like": envtests._is_string_like,
    "subclass": is_subclass,
    "instance": is_instance,
    # "match": envtests.regex_match,
    # "search": envtests.regex_search,
    "contains": operator.contains,
}
