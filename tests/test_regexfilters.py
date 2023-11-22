from __future__ import annotations

from jinja2.exceptions import FilterArgumentError
from jinjarope import regexfilters
import pytest


def test_re_replace():
    assert (
        regexfilters.re_replace("Hello, World!", "World", "Universe")
        == "Hello, Universe!"
    )
    assert (
        regexfilters.re_replace("Hello, World!", "world", "Universe", ignorecase=True)
        == "Hello, Universe!"
    )
    assert (
        regexfilters.re_replace(
            "Hello, World! Hello, World!",
            "World",
            "Universe",
            count=1,
        )
        == "Hello, Universe! Hello, World!"
    )


def test_re_findall():
    assert regexfilters.re_findall("Hello, World! Hello, Universe!", "Hello") == [
        "Hello",
        "Hello",
    ]
    assert regexfilters.re_findall(
        "Hello, World! Hello, Universe!",
        "hello",
        ignorecase=True,
    ) == ["Hello", "Hello"]
    assert regexfilters.re_findall("Hello, World! Hello, Universe!", "Goodbye") == []


def test_re_search():
    assert regexfilters.re_search("Hello, World! Hello, Universe!", "World") == "World"
    assert (
        regexfilters.re_search("Hello, World! Hello, Universe!", "world", ignorecase=True)
        == "World"
    )
    assert regexfilters.re_search("Hello, World! Hello, Universe!", "Goodbye") is None
    assert regexfilters.re_search("A\nB", "^B", multiline=True)
    with pytest.raises(FilterArgumentError):
        regexfilters.re_search("A\nB", "^B", "x")


def test_re_escape():
    assert regexfilters.re_escape("Hello, World!") == "Hello,\\ World!"
    assert regexfilters.re_escape("Hello, World!", "posix_basic") == "Hello, World!"
    assert regexfilters.re_escape("[a]", "posix_basic") == "\\[a\\]"
    with pytest.raises(NotImplementedError):
        regexfilters.re_escape("Hello, World!", "unknown")
