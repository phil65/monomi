from __future__ import annotations

from collections.abc import Callable, Iterator
import functools
import logging
import os

from typing import Any, TypeVar


logger = logging.getLogger(__name__)

ClassType = TypeVar("ClassType", bound=type)


def iter_subclasses(klass: ClassType) -> Iterator[ClassType]:
    """(Recursively) iterate all subclasses of given klass.

    Arguments:
        klass: class to get subclasses from
    """
    for kls in klass.__subclasses__():
        yield from iter_subclasses(kls)
        yield kls


def get_repr(_obj: Any, *args: Any, **kwargs: Any) -> str:
    """Get a suitable __repr__ string for an object.

    Args:
        _obj: The object to get a repr for.
        *args: Arguments for the repr
        **kwargs: Keyword arguments for the repr
    """
    classname = type(_obj).__name__
    parts = [repr(v) for v in args]
    kw_parts = []
    for k, v in kwargs.items():
        kw_parts.append(f"{k}={v!r}")
    sig = ", ".join(parts + kw_parts)
    return f"{classname}({sig})"


@functools.cache
def fsspec_get(path: str) -> str:
    """Fetch a file via fsspec and return file content as a string.

    Arguments:
        path: The path to fetch the file from
    """
    import fsspec

    with fsspec.open(path) as file:
        return file.read().decode()


T = TypeVar("T")


@functools.lru_cache(maxsize=1)
def _get_black_formatter() -> Callable[[str, int], str]:
    """Return a formatter.

    If black is available, a callable to format code using black is returned,
    otherwise a noop callable is returned.
    """
    try:
        from black import InvalidInput, Mode, format_str
    except ModuleNotFoundError:
        logger.info("Formatting signatures requires Black to be installed.")
        return lambda text, _: text

    def formatter(code: str, line_length: int) -> str:
        mode = Mode(line_length=line_length)
        try:
            return format_str(code, mode=mode)
        except InvalidInput:
            return code

    return formatter


def format_code(code: str, line_length: int = 100):
    """Format code to given line length using `black`.

    Arguments:
        code: The code to format
        line_length: Line length limit for formatted code
    """
    code = code.strip()
    if len(code) < line_length:
        return code
    formatter = _get_black_formatter()
    return formatter(code, line_length)


def get_hash(obj: Any, hash_length: int | None = 7) -> str:
    """Get a Md5 hash for given object.

    Arguments:
        obj: The object to get a hash for ()
        hash_length: Optional cut-off value to limit length
    """
    import hashlib

    hash_md5 = hashlib.md5(str(obj).encode("utf-8"))
    return hash_md5.hexdigest()[:hash_length]


def slugify(text: str | os.PathLike) -> str:
    """Create a slug for given text.

    Returned text only contains alphanumerical and underscore.

    Arguments:
        text: text to get a slug for
    """
    import re

    text = str(text).lower()
    text = re.sub("[^0-9a-zA-Z_.]", "_", text)
    return re.sub("^[^0-9a-zA-Z_#]+", "", text)


if __name__ == "__main__":
    code = "def test(sth, fsjkdalfjksdalfjsadk, fjskldjfkdsljf, fsdkjlafjkdsafj): pass"
    result = format_code(code, line_length=50)
    print(result)
