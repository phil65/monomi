from __future__ import annotations

from jinjarope import textfilters


GIVEN = """def test(sth, averylongvarname, anotherlongvarname, andanother): pass"""
EXPECTED = """\
def test(
    sth,
    averylongvarname,
    anotherlongvarname,
    andanother,
):
    pass
"""


def test_removesuffix():
    assert textfilters.removesuffix("Hello, World!", ", World!") == "Hello"


def test_removeprefix():
    assert textfilters.removeprefix("Hello, World!", "Hello, ") == "World!"


def test_lstrip():
    assert textfilters.lstrip("   Hello, World!  ") == "Hello, World!  "  # noqa: B005


def test_rstrip():
    assert textfilters.rstrip("   Hello, World!  ") == "   Hello, World!"  # noqa: B005


def test_format_code():
    assert textfilters.format_code(GIVEN, line_length=50) == EXPECTED


def test_format_signature():
    def test_function(a, b, c: int = 1, *args, **kwargs):
        pass

    assert (
        textfilters.format_signature(test_function)
        == "(a, b, c: int = 1, *args, **kwargs)"
    )
    assert (
        textfilters.format_signature(test_function, eval_str=False)
        == "(a, b, c: 'int' = 1, *args, **kwargs)"
    )


def test_slugify():
    assert textfilters.slugify("Hello, World!") == "hello__world_"


if __name__ == "__main__":
    code = "def test(sth, fsjkdalfjksdalfjsadk, fjskldjfkdsljf, fsdkjlafjkdsafj): pass"
    text = textfilters.format_code(code, line_length=50)
    print(text)
