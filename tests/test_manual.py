from __future__ import annotations

from jinjarope import manual
import mknodes as mk


def test_building_the_docs():
    build = manual.Build()
    nav = mk.MkNav()
    build.on_root(nav)
    assert nav.children
    for node in nav.descendants:
        if isinstance(node, mk.MkPage):
            str(node)
