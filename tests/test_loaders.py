from __future__ import annotations

import jinjarope


def test_prefix_loader():
    loader = "test" / jinjarope.DictLoader({"a": "b"})
    env = jinjarope.Environment(loader=loader)
    assert env.render_template("test/a") == "b"
    assert "test/a" in loader
    loader1 = jinjarope.PrefixLoader({"prefix": jinjarope.DictLoader({})})
    loader2 = jinjarope.PrefixLoader({"prefix": jinjarope.DictLoader({})})
    assert loader1 == loader2
    assert len({loader1, loader2}) == 1
    assert repr(loader1)


def test_function_loader():
    def load_fn(path: str) -> str:
        return "abc"

    loader1 = jinjarope.FunctionLoader(load_fn)
    loader2 = jinjarope.FunctionLoader(load_fn)
    assert loader1 == loader2
    assert len({loader1, loader2}) == 1
    assert repr(loader1)


def test_packageloader():
    loader1 = jinjarope.PackageLoader("jinjarope")
    loader2 = jinjarope.PackageLoader(jinjarope)
    assert loader1 == loader2
    assert len({loader1, loader2}) == 1
    assert repr(loader1)


def test_filesystemloader():
    loader1 = jinjarope.FileSystemLoader("")
    loader2 = jinjarope.FileSystemLoader("")
    assert loader1 == loader2
    assert len({loader1, loader2}) == 1
    assert repr(loader1)
