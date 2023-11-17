from __future__ import annotations

from collections.abc import Sequence
import configparser
import datetime
import functools

from importlib import metadata
import io
import json
import logging
import os
import pathlib
import platform
import sys
from typing import Any, Literal

from jinjarope import jinjafile, utils


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


_cache: dict[str, str] = {}


def get_output_from_call(
    call: str | Sequence[str],
    cwd: str | os.PathLike | None = None,
    use_cache: bool = False,
) -> str | None:
    """Execute a system call and return its output as a string.

    Arguments:
        call: The system call to make
        cwd: The working directory for the call
        use_cache: Whether to cache the output of calls
    """
    import pathlib
    import subprocess

    if not call:
        return None
    if not isinstance(call, str):
        call = " ".join(call)
    key = pathlib.Path(cwd or ".").absolute().as_posix() + call
    if key in _cache and use_cache:
        return _cache[key]
    msg = f"Executing {call!r}..."
    logger.info(msg)
    try:
        pipe = subprocess.PIPE
        text = subprocess.run(call, stdout=pipe, text=True, shell=True, cwd=cwd).stdout
        _cache[key] = text
        return text  # noqa: TRY300
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


def is_instance(obj: object, typ: str | type) -> bool:
    kls = utils.resolve(typ) if isinstance(typ, str) else typ
    if not isinstance(kls, type):
        raise TypeError(kls)
    return isinstance(obj, kls)


def is_subclass(obj: type, typ: str | type) -> bool:
    kls = utils.resolve(typ) if isinstance(typ, str) else typ
    if not isinstance(kls, type):
        raise TypeError(kls)
    return issubclass(obj, kls)


def has_internet() -> bool:
    import http.client as httplib

    conn = httplib.HTTPSConnection("8.8.8.8", timeout=2)
    try:
        conn.request("HEAD", "/")
        return True  # noqa: TRY300
    except Exception:  # noqa: BLE001
        return False
    finally:
        conn.close()


def now(tz: datetime.tzinfo | None = None) -> datetime.datetime:
    """Get current Datetime.

    Arguments:
        tz: timezone for retuned datetime
    """
    return datetime.datetime.now(tz)


def utcnow() -> datetime.datetime:
    """Get UTC datetime."""
    return datetime.datetime.utcnow()


ENV_GLOBALS = {
    "online": has_internet,
    "now": datetime.datetime.now,
    "cwd": pathlib.Path.cwd,
    "utcnow": datetime.datetime.utcnow,
    "environment": version_info,
    "JinjaFile": jinjafile.JinjaFile,
}
