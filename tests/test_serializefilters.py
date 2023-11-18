from __future__ import annotations

from jinjarope import serializefilters


def test_serialize_deserialize():
    text = {"abc": {"def": "ghi"}}
    for fmt in ("yaml", "json", "ini", "toml"):
        assert (
            serializefilters.deserialize(serializefilters.serialize(text, fmt), fmt)
            == text
        )
