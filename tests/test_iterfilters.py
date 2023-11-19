from __future__ import annotations

from jinjarope import iterfilters


def test_reduce_list():
    assert iterfilters.reduce_list([1, 2, 2, 3, 4, 4, 4, 5]) == [1, 2, 3, 4, 5]
    assert iterfilters.reduce_list([]) == []
    assert iterfilters.reduce_list(["a", "b", "b", "c"]) == ["a", "b", "c"]


def test_flatten_dict():
    assert iterfilters.flatten_dict({"a": {"b": {"c": "d"}}}) == {"a/b/c": "d"}
    assert iterfilters.flatten_dict({"a": {"b": "c"}, "d": "e"}) == {"a/b": "c", "d": "e"}
    assert iterfilters.flatten_dict({}) == {}


def test_batched():
    assert list(iterfilters.batched("ABCDEFG", 3)) == [
        ("A", "B", "C"),
        ("D", "E", "F"),
        ("G",),
    ]
    assert list(iterfilters.batched([], 3)) == []
    assert list(iterfilters.batched([1, 2, 3, 4, 5], 2)) == [(1, 2), (3, 4), (5,)]


def test_natsort():
    assert iterfilters.natsort(["A1", "B1", "A2", "A10"], key=lambda x: x) == [
        "A1",
        "A2",
        "A10",
        "B1",
    ]
    assert iterfilters.natsort([], key=lambda x: x) == []
    assert iterfilters.natsort(["B1", "A1"], key=lambda x: x, reverse=True) == [
        "B1",
        "A1",
    ]


def test_do_any():
    assert iterfilters.do_any([True, False, False]) is True
    assert iterfilters.do_any([False, False, False]) is False
    assert iterfilters.do_any([]) is False
    assert iterfilters.do_any([0, 1, 2], attribute="real") is True


def test_groupby_first_letter():
    data = ["apple", "banana", "cherry", "avocado", "carrot", "blueberry"]
    grouped = iterfilters.groupby_first_letter(data)
    assert grouped == {
        "A": ["apple", "avocado"],
        "B": ["banana", "blueberry"],
        "C": ["carrot", "cherry"],
    }


def test_groupby_first_letter_with_empty_data():
    data = []
    grouped = iterfilters.groupby_first_letter(data)
    assert grouped == {}
