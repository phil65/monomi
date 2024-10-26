from __future__ import annotations

import pytest

from jinjarope import envglobals


def test_match():
    assert envglobals.match("a", a="hit", b="miss") == "hit"


if __name__ == "__main__":
    pytest.main([__file__])
