from __future__ import annotations

from collections.abc import Iterator
import functools
import inspect
import logging

from typing import Any, TypeVar


logger = logging.getLogger(__name__)

ClassType = TypeVar("ClassType", bound=type)


@functools.cache
def list_subclasses(
    klass: ClassType,
    *,
    recursive: bool = True,
    filter_abstract: bool = False,
    filter_generic: bool = True,
    filter_locals: bool = True,
) -> list[ClassType]:
    """Return list of all subclasses of given klass.

    Note: This call is cached. Consider iter_subclasses for uncached iterating.

    Arguments:
        klass: class to get subclasses from
        filter_abstract: whether abstract base classes should be included.
        filter_generic: whether generic base classes should be included.
        filter_locals: whether local base classes should be included.
        recursive: whether to also get subclasses of subclasses.
    """
    return list(
        iter_subclasses(
            klass,
            recursive=recursive,
            filter_abstract=filter_abstract,
            filter_generic=filter_generic,
            filter_locals=filter_locals,
        ),
    )


def iter_subclasses(
    klass: ClassType,
    *,
    recursive: bool = True,
    filter_abstract: bool = False,
    filter_generic: bool = True,
    filter_locals: bool = True,
) -> Iterator[ClassType]:
    """(Recursively) iterate all subclasses of given klass.

    Arguments:
        klass: class to get subclasses from
        filter_abstract: whether abstract base classes should be included.
        filter_generic: whether generic base classes should be included.
        filter_locals: whether local base classes should be included.
        recursive: whether to also get subclasses of subclasses.
    """
    if getattr(klass.__subclasses__, "__self__", None) is None:
        return
    for kls in klass.__subclasses__():
        if recursive:
            yield from iter_subclasses(
                kls,
                filter_abstract=filter_abstract,
                filter_generic=filter_generic,
                filter_locals=filter_locals,
            )
        if filter_abstract and inspect.isabstract(kls):
            continue
        if filter_generic and kls.__qualname__.endswith("]"):
            continue
        if filter_locals and "<locals>" in kls.__qualname__:
            continue
        yield kls


@functools.cache
def list_baseclasses(
    klass: ClassType,
    *,
    recursive: bool = True,
    filter_abstract: bool = False,
    filter_generic: bool = True,
    filter_locals: bool = True,
) -> list[ClassType]:
    """Return list of all baseclasses of given klass.

    Arguments:
        klass: class to get subclasses from
        filter_abstract: whether abstract base classes should be included.
        filter_generic: whether generic base classes should be included.
        filter_locals: whether local base classes should be included.
        recursive: whether to also get baseclasses of baseclasses.
    """
    return list(
        iter_baseclasses(
            klass,
            recursive=recursive,
            filter_abstract=filter_abstract,
            filter_generic=filter_generic,
            filter_locals=filter_locals,
        ),
    )


def iter_baseclasses(
    klass: ClassType,
    *,
    recursive: bool = True,
    filter_abstract: bool = False,
    filter_generic: bool = True,
    filter_locals: bool = True,
) -> Iterator[ClassType]:
    """(Recursively) iterate all baseclasses of given klass.

    Arguments:
        klass: class to get subclasses from
        filter_abstract: whether abstract base classes should be included.
        filter_generic: whether generic base classes should be included.
        filter_locals: whether local base classes should be included.
        recursive: whether to also get baseclasses of baseclasses.
    """
    for kls in klass.__bases__:
        if recursive:
            yield from iter_baseclasses(
                kls,
                recursive=recursive,
                filter_abstract=filter_abstract,
                filter_generic=filter_generic,
                filter_locals=filter_locals,
            )
        if filter_abstract and inspect.isabstract(kls):
            continue
        if filter_generic and kls.__qualname__.endswith("]"):
            continue
        if filter_locals and "<locals>" in kls.__qualname__:
            continue
        yield kls


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
