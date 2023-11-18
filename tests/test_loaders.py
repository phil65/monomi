from __future__ import annotations

import jinjarope


def test_prefix_loader_eq():
    loader1 = jinjarope.PrefixLoader({"prefix": jinjarope.DictLoader({})})
    loader2 = jinjarope.PrefixLoader({"prefix": jinjarope.DictLoader({})})
    assert loader1 == loader2


def test_package_loader_init_with_module():
    loader = jinjarope.PackageLoader(jinjarope)
    assert loader.package_name == "jinjarope"


def test_package_loader_init_with_string():
    loader = jinjarope.PackageLoader("jinjarope")
    assert loader.package_name == "jinjarope"
