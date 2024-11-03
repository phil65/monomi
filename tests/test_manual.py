from __future__ import annotations

import os

import mknodes as mk
import pytest

from jinjarope import manual


@pytest.mark.skipif(not os.environ.get("CI"), reason="Test only runs in CI")
def test_building_the_docs():
    build = manual.Build()
    nav = mk.MkNav()
    build.on_root(nav)
    assert nav.children
    for node in nav.descendants:
        if isinstance(node, mk.MkPage):
            str(node)


if __name__ == "__main__":
    pytest.main([__file__])
