from __future__ import annotations

import ast

from collections.abc import Sequence
import contextlib
import datetime
import functools
import importlib
from importlib import metadata
import io
import json
import logging
import os
import pathlib
import platform
import pprint
import sys
import time
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


def format_js_map(dct: dict, indent: int = 4) -> str:
    """Return JS map str for given dictionary.

    Arguments:
        dct: Dictionary to dump
        indent: The amount of indentation for the key-value pairs
    """
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


def evaluate(
    code: str,
    context: dict[str, Any] | None = None,
) -> str:
    """Evaluate python code and return the caught stdout + return value of last line.

    Arguments:
        code: The code to execute
        context: Globals for the execution evironment
    """
    import mknodes as mk

    now = time.time()
    if context is None:
        context = {"mk": mk}
    logger.debug("Evaluating code:\n%s", code)
    tree = ast.parse(code)
    eval_expr = ast.Expression(tree.body[-1].value)  # type: ignore
    # exec_expr = ast.Module(tree.body[:-1])  # type: ignore
    exec_expr = ast.parse("")
    exec_expr.body = tree.body[:-1]
    compiled = compile(exec_expr, "file", "exec")
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exec(compiled, context)
        val = eval(compile(eval_expr, "file", "eval"), context)
    logger.debug("Code evaluation took %s seconds.", time.time() - now)
    # result = mk.MkContainer([buffer.getvalue(), val])
    return val or ""


def add(text, prefix: str = "", suffix: str = ""):
    if not text:
        return ""
    return f"{prefix}{text}{suffix}"


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
    "add": add,
    "issubclass": issubclass,
    "isinstance": isinstance,
    "import_module": importlib.import_module,
    "hasattr": hasattr,
    "evaluate": evaluate,
    "partial": functools.partial,
    "dump_json": json.dumps,
    "load_json": json.loads,
    "load_toml": tomllib.loads,
    "load_file": load_file_cached,
    "path_join": os.path.join,
    "format_js_map": format_js_map,
    "check_output": get_output_from_call,
    "getenv": os.getenv,
}


if __name__ == "__main__":
    a = evaluate("import mknodes\nmknodes.MkHeader('Hello')")
    print(a)
