from __future__ import annotations

from jinjarope import serializefilters


def test_serialize_deserialize():
    text = {"abc": {"def": "ghi"}}
    for fmt in ("yaml", "json", "ini", "toml"):
        assert (
            serializefilters.deserialize(serializefilters.serialize(text, fmt), fmt)
            == text
        )


def test_dig():
    data = {
        "section1": {
            "section2": {
                "section3": "Hello, World!",
            },
        },
    }
    assert (
        serializefilters.dig(data, "section1", "section2", "section3") == "Hello, World!"
    )
    assert serializefilters.dig(data, "section1", "section2", "nonexistent") is None


def test_dig_with_list():
    data = {
        "section1": [
            {"section1": "Wrong one!"},
            {"section2": "Hello, World!"},
        ],
    }
    assert serializefilters.dig(data, "section1", "section2") == "Hello, World!"


def test_dig_with_keep_path():
    data = {
        "section1": {
            "section2": {
                "section3": "Hello, World!",
                "something": "else!",
            },
        },
    }
    assert serializefilters.dig(
        data,
        "section1",
        "section2",
        "section3",
        keep_path=True,
    ) == {
        "section1": {"section2": {"section3": "Hello, World!"}},
    }


def test_dig_with_keep_path_and_list():
    # TODO: this behaviour needs to get implemented correctly.
    data = {
        "section1": [
            {"section1": "Wrong one!"},
            {"section2": "Hello, World!"},
        ],
    }
    assert serializefilters.dig(data, "section1", "section2", keep_path=True) == {
        "section1": {"section2": "Hello, World!"},
    }
