from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
import functools
import importlib

from importlib.metadata import entry_points
import logging
import types
from typing import Any, TypeVar

from jinjarope import envtests


logger = logging.getLogger(__name__)

ClassType = TypeVar("ClassType", bound=type)


def partial(fn: Callable, *args: Any, **kwargs: Any):
    """Create new function with partial application of given arguments / keywords.

    Arguments:
        fn: The function to generate a partial from
        args: patially applied arguments
        kwargs: partially applied keywords
    """
    return functools.partial(fn, *args, **kwargs)


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

    Arguments:
        _obj: The object to get a repr for.
        args: Arguments for the repr
        kwargs: Keyword arguments for the repr
    """
    classname = type(_obj).__name__
    parts = [repr(v) for v in args]
    kw_parts = [f"{k}={v!r}" for k, v in kwargs.items()]
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


@functools.lru_cache
def _entry_points(group: str) -> Mapping[str, Callable]:
    eps = {ep.name: ep.load() for ep in entry_points(group=group)}
    logger.debug("Available %r entry points: %s", group, sorted(eps))
    return eps


def get_hash(obj: Any, hash_length: int | None = 7) -> str:
    """Get a Md5 hash for given object.

    Arguments:
        obj: The object to get a hash for ()
        hash_length: Optional cut-off value to limit length
    """
    import hashlib

    hash_md5 = hashlib.md5(str(obj).encode("utf-8"))
    return hash_md5.hexdigest()[:hash_length]


@functools.cache
def resolve(name: str, module: str | None = None) -> types.ModuleType | Callable:
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
    if envtests.is_python_builtin(used):
        import builtins

        return getattr(builtins, used)
    found = importlib.import_module(used)
    for n in names:
        used += "." + n
        try:
            found = getattr(found, n)
        except AttributeError:
            try:
                importlib.import_module(used)
                found = getattr(found, n)
            except ModuleNotFoundError:
                mod = ".".join(used.split(".")[:-1])
                importlib.import_module(mod)
                found = getattr(found, n)
    return found


@functools.cache
def get_doc(
    obj: Any,
    *,
    escape: bool = False,
    fallback: str = "",
    from_base_classes: bool = False,
    only_summary: bool = False,
    only_description: bool = False,
) -> str:
    """Get __doc__ for given object.

    Arguments:
        obj: Object to get docstrings from
        escape: Whether docstrings should get escaped
        fallback: Fallback in case docstrings dont exist
        from_base_classes: Use base class docstrings if docstrings dont exist
        only_summary: Only return first line of docstrings
        only_description: Only return block after first line
    """
    import inspect

    from jinjarope import mdfilters

    match obj:
        case _ if from_base_classes:
            doc = inspect.getdoc(obj)
        case _ if obj.__doc__:
            doc = inspect.cleandoc(obj.__doc__)
        case _:
            doc = None
    if not doc:
        return fallback
    if only_summary:
        doc = doc.split("\n")[0]
    if only_description:
        doc = "\n".join(doc.split("\n")[1:])
    return mdfilters.md_escape(doc) if doc and escape else doc


if __name__ == "__main__":
    doc = get_doc(str)
