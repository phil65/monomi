from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
import functools

from typing import Any, TypeVar


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
    import fsspec

    with fsspec.open(path) as file:
        return file.read().decode()


T = TypeVar("T")


def reduce_list(data_set: Iterable[T]) -> list[T]:
    """Reduce duplicate items in a list and preserve order."""
    return list(dict.fromkeys(data_set))


def flatten_dict(dct: Mapping, sep: str = "/", parent_key: str = "") -> Mapping:
    items: list[tuple[str, str]] = []
    for k, v in dct.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, Mapping):
            items.extend(flatten_dict(v, parent_key=new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
