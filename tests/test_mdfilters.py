from __future__ import annotations

from jinjarope import mdfilters


def test_md_link():
    assert (
        mdfilters.md_link("GitHub", "http://github.com") == "[GitHub](http://github.com)"
    )
    assert (
        mdfilters.md_link("GitHub", "http://github.com", "GitHub homepage")
        == "[GitHub](http://github.com 'GitHub homepage')"
    )
    assert mdfilters.md_link("GitHub", "") == "GitHub"
    assert mdfilters.md_link("GitHub", None) == "GitHub"
    assert (
        mdfilters.md_link(None, "http://github.com")
        == "[http://github.com](http://github.com)"
    )
    assert mdfilters.md_link(None, None) == ""


def test_extract_header_section():
    markdown = """\
# Section 1
Content 1
## Subsection 1
Content 1.1
# Section 2
Content 2
"""
    assert (
        mdfilters.extract_header_section(markdown, "Section 1")
        == "Content 1\n## Subsection 1\nContent 1.1\n"
    )
    assert mdfilters.extract_header_section(markdown, "Section 2") == "Content 2\n"
    assert mdfilters.extract_header_section(markdown, "Section 3") is None


def test_md_escape():
    assert mdfilters.md_escape("Hello, World!") == "Hello, World\\!"
    assert mdfilters.md_escape("Hello, World!", "pre") == "Hello, World!"
    assert mdfilters.md_escape("Hello, World!", "code") == "Hello, World!"
    assert mdfilters.md_escape("Hello, World!", "text_link") == "Hello, World!"
    assert (
        mdfilters.md_escape("_*[]()~`>#+-=|{}.!")
        == "\\_\\*\\[\\]\\(\\)\\~\\`\\>\\#\\+\\-\\=\\|\\{\\}\\.\\!"
    )


def test_md_style():
    assert mdfilters.md_style("Hello, World!") == "Hello, World!"
    assert (
        mdfilters.md_style("Hello, World!", size=3)
        == "<font size='3'>Hello, World!</font>"
    )
    assert mdfilters.md_style("Hello, World!", bold=True) == "**Hello, World!**"
    assert mdfilters.md_style("Hello, World!", italic=True) == "*Hello, World!*"
    assert mdfilters.md_style("Hello, World!", code=True) == "`Hello, World!`"
    assert (
        mdfilters.md_style("Hello, World!", align="center")
        == "<p style='text-align: center;'>Hello, World!</p>"
    )
    assert (
        mdfilters.md_style(
            "Hello, World!",
            size=3,
            bold=True,
            italic=True,
            code=True,
            align="center",
        )
        == "<p style='text-align: center;'>`***<font size='3'>Hello,"
        " World!</font>***`</p>"
    )
