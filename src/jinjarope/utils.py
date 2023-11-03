from __future__ import annotations

from collections.abc import Iterable
import functools

from typing import Any, TypeVar


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
    import fsspec

    with fsspec.open(path) as file:
        return file.read().decode()


T = TypeVar("T")


def reduce_list(data_set: Iterable[T]) -> list[T]:
    """Reduce duplicate items in a list and preserve order."""
    return list(dict.fromkeys(data_set))
