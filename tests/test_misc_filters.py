from __future__ import annotations

from jinjarope import envglobals


def test_match():
    assert envglobals.match("a", a="hit", b="miss") == "hit"
