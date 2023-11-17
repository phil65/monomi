from __future__ import annotations

from collections.abc import Callable, Generator, Iterable, Mapping
import itertools

from typing import TypeVar


T = TypeVar("T")


def pairwise(items: Iterable[T]) -> itertools.pairwise[tuple[T, T]]:
    """Return an iterator of overlapping pairs taken from the input iterator.

    s -> (s0,s1), (s1,s2), (s2, s3), ...

    Arguments:
        items: The items to iter pair-wise
    """
    return itertools.pairwise(items)


def do_zip(*items: Iterable[T]) -> zip:
    """Zip iterables into a single one.

    Arguments:
        items: The iterables to zip
    """
    return zip(*items)


def reduce_list(items: Iterable[T]) -> list[T]:
    """Reduce duplicate items in a list and preserve order.

    Arguments:
        items: The iterable to recude to a unique-item list
    """
    return list(dict.fromkeys(items))


def flatten_dict(dct: Mapping, sep: str = "/", _parent_key: str = "") -> Mapping:
    """Flatten a nested dictionary to a flat one.

    The individual parts of the "key path" are joined with given separator.

    Arguments:
        dct: The dictionary to flatten
        sep: The separator to use for joining
    """
    items: list[tuple[str, str]] = []
    for k, v in dct.items():
        new_key = _parent_key + sep + k if _parent_key else k
        if isinstance(v, Mapping):
            items.extend(flatten_dict(v, _parent_key=new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def batched(iterable: Iterable[T], n: int) -> Generator[tuple[T, ...], None, None]:
    """Batch data into tuples of length n. The last batch may be shorter.

    Examples:
        ``` py
        batched('ABCDEFG', 3)  # returns ABC DEF G
        ```

    Arguments:
        iterable: The iterable to yield as batches
        n: The batch size
    """
    if n < 1:
        msg = "n must be at least one"
        raise ValueError(msg)
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch


def natsort(
    val: Iterable[T],
    key: str | Callable | None = None,
    reverse: bool = False,
    ignore_case: bool = True,
) -> Iterable[T]:
    """Using the natsort package, sort a list naturally.

    i.e. A1, B1, A2, A10 will sort A1, A2, A10, B1.

    Arguments:
        val: the iterable to sort
        key: If str, sort by attribute with given name. If callable, use it as keygetter.
             If None, sort by objects itself
        reverse: Whether to reverse the sort order
        ignore_case: Whether to ignore case for sorting
    """
    from operator import attrgetter

    from natsort import natsorted, ns

    alg = ns.IGNORECASE
    if not ignore_case:
        alg = ns.LOWERCASEFIRST
    return natsorted(
        val,
        key=attrgetter(key) if isinstance(key, str) else key,
        reverse=reverse,
        alg=alg,
    )


def do_any(seq: Iterable, attribute: str | None = None) -> bool:
    """Check if at least one of the item in the sequence evaluates to true.

    The `any` builtin as a filter for Jinja templates.

    Arguments:
        seq: An iterable object.
        attribute: The attribute name to use on each object of the iterable.

    Returns:
        A boolean telling if any object of the iterable evaluated to True.
    """
    if attribute is None:
        return any(seq)
    return any(getattr(i, attribute) for i in seq)
