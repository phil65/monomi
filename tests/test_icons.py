from __future__ import annotations

import pytest

from jinjarope import iconfilters


def test_material_key_conversion():
    assert iconfilters.get_pyconify_key("file") == "mdi:file"
    assert iconfilters.get_pyconify_key("mdi:file") == "mdi:file"
    assert iconfilters.get_pyconify_key("material/file") == "mdi:file"
    assert iconfilters.get_pyconify_key(":material-file:") == "mdi:file"


def test_noto_key_conversion():
    assert iconfilters.get_pyconify_key("noto:wrench") == "noto:wrench"
    assert iconfilters.get_pyconify_key(":noto-wrench:") == "noto:wrench"
    assert (
        iconfilters.get_pyconify_key("simple/shieldsdotio") == "simple-icons:shieldsdotio"
    )
    assert (
        iconfilters.get_pyconify_key(":fontawesome-regular-keyboard:")
        == "fa6-regular:keyboard"
    )
    assert (
        iconfilters.get_pyconify_key("fontawesome/regular/keyboard")
        == "fa6-regular:keyboard"
    )


if __name__ == "__main__":
    pytest.main([__file__])
