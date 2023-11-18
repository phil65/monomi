from __future__ import annotations

from xml.etree import ElementTree as Et

from jinjarope import htmlfilters
import pytest


def test_wrap_in_elem():
    assert htmlfilters.wrap_in_elem("Hello", "p") == "<p>Hello</p>"
    assert (
        htmlfilters.wrap_in_elem("Hello", "p", add_linebreaks=True) == "<p>\nHello\n</p>"
    )
    assert (
        htmlfilters.wrap_in_elem("Hello", "p", id="greeting", class_="greet")
        == '<p id="greeting" class="greet">Hello</p>'
    )
    assert htmlfilters.wrap_in_elem("", "p") == ""
    assert htmlfilters.wrap_in_elem(None, "p") == ""


def test_html_link():
    assert (
        htmlfilters.html_link("Google", "http://google.com")
        == "<a href='http://google.com'>Google</a>"
    )
    assert htmlfilters.html_link("Google", "") == "Google"
    assert htmlfilters.html_link("Google", None) == "Google"
    assert (
        htmlfilters.html_link(None, "http://google.com")
        == "<a href='http://google.com'>http://google.com</a>"
    )
    assert htmlfilters.html_link(None, None) == ""


def test_format_js_map():
    assert htmlfilters.format_js_map({"key": "value"}) == "{\n    key: 'value',\n}"
    assert htmlfilters.format_js_map('{"key": "value"}') == "{\n    key: 'value',\n}"
    assert htmlfilters.format_js_map({"key": True}) == "{\n    key: true,\n}"
    assert htmlfilters.format_js_map({"key": None}) == "{\n    key: null,\n}"
    assert (
        htmlfilters.format_js_map({"key": {"nested_key": "nested_value"}})
        == "{\n    key: {\n    nested_key: 'nested_value',\n},\n}"
    )


def test_svg_to_data_uri():
    assert (
        htmlfilters.svg_to_data_uri("<svg></svg>")
        == "url('data:image/svg+xml;charset=utf-8,<svg></svg>')"
    )
    assert htmlfilters.svg_to_data_uri("") == "url('data:image/svg+xml;charset=utf-8,')"
    with pytest.raises(TypeError):
        htmlfilters.svg_to_data_uri(None)


def test_clean_svg():
    assert (
        htmlfilters.clean_svg(
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?><svg></svg>',
        )
        == "<svg></svg>"
    )
    assert (
        htmlfilters.clean_svg(
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"'
            ' "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg></svg>',
        )
        == "<svg></svg>"
    )
    assert htmlfilters.clean_svg("<svg></svg>") == "<svg></svg>"
    assert htmlfilters.clean_svg("") == ""


def test_format_css_rule():
    assert htmlfilters.format_css_rule({".a": {"b": "c"}}) == ".a {\n\tb: c;\n}\n\n"
    assert (
        htmlfilters.format_css_rule({".a": {"b": "c", "d": "e"}})
        == ".a {\n\tb: c;\n\td: e;\n}\n\n"
    )
    assert (
        htmlfilters.format_css_rule({".a": {"b": {"c": "d"}}}) == ".a b {\n\tc: d;\n}\n\n"
    )
    assert htmlfilters.format_css_rule({}) == ""


def test_format_xml_with_str():
    xml_str = "<root><child>text</child></root>"
    formatted_xml = htmlfilters.format_xml(xml_str)
    expected_xml = "<root>\n  <child>text</child>\n</root>"
    assert formatted_xml == expected_xml


def test_format_xml_with_element():
    xml_elem = Et.Element("root")
    child = Et.SubElement(xml_elem, "child")
    child.text = "text"
    formatted_xml = htmlfilters.format_xml(xml_elem)
    expected_xml = "<root>\n  <child>text</child>\n</root>"
    assert formatted_xml == expected_xml


def test_format_xml_with_indent():
    xml_str = "<root><child>text</child></root>"
    formatted_xml = htmlfilters.format_xml(xml_str, indent=4)
    expected_xml = "<root>\n    <child>text</child>\n</root>"
    assert formatted_xml == expected_xml


def test_format_xml_with_level():
    xml_str = "<root><child>text</child></root>"
    formatted_xml = htmlfilters.format_xml(xml_str, level=1)
    # IMO missing indent at beginning this is unexpected, but thats what ET returns..
    expected_xml = "<root>\n    <child>text</child>\n  </root>"
    assert formatted_xml == expected_xml
