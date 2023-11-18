from __future__ import annotations

from collections.abc import Mapping
import json
import re

from typing import Any, Literal
from xml.etree import ElementTree as Et


def wrap_in_elem(
    text: str | None,
    tag: str,
    add_linebreaks: bool = False,
    **kwargs: Any,
) -> str:
    """Wrap given text in an HTML/XML tag (with attributes).

    If text is empty, just return an empty string.

    Arguments:
        text: Text to wrap
        tag: Tag to wrap text in
        add_linebreaks: Adds a linebreak before and after the text
        kwargs: additional key-value pairs to be inserted as attributes for tag.
                Key strings will have "_" stripped from the end to allow using keywords.
    """
    if not text:
        return ""
    attrs = [f'{k.rstrip("_")}="{v}"' for k, v in kwargs.items()]
    attr_str = (" " + " ".join(attrs)) if attrs else ""
    nl = "\n" if add_linebreaks else ""
    return f"<{tag}{attr_str}>{nl}{text}{nl}</{tag}>"


def html_link(text: str | None = None, link: str | None = None, **kwargs: Any) -> str:
    """Create a html link.

    If link is empty string or None, just the text will get returned.

    Arguments:
        text: Text to show for the link
        link: Target url
        kwargs: additional key-value pairs to be inserted as attributes.
                Key strings will have "_" stripped from the end to allow using keywords.
    """
    if not link:
        return text or ""
    attrs = [f'{k.rstrip("_")}="{v}"' for k, v in kwargs.items()]
    attr_str = (" " + " ".join(attrs)) if attrs else ""
    return f"<a href={link!r}{attr_str}>{text or link}</a>"


def format_js_map(mapping: dict | str, indent: int = 4) -> str:
    """Return JS map str for given dictionary.

    Arguments:
        mapping: Dictionary to dump
        indent: The amount of indentation for the key-value pairs
    """
    dct = json.loads(mapping) if isinstance(mapping, str) else mapping
    rows = []
    indent_str = " " * indent
    for k, v in dct.items():
        match v:
            case bool():
                rows.append(f"{indent_str}{k}: {str(v).lower()},")
            case dict():
                rows.append(f"{indent_str}{k}: {format_js_map(v)},")
            case None:
                rows.append(f"{indent_str}{k}: null,")
            case _:
                rows.append(f"{indent_str}{k}: {v!r},")
    row_str = "\n" + "\n".join(rows) + "\n"
    return f"{{{row_str}}}"


def svg_to_data_uri(svg: str) -> str:
    """Wrap svg as data URL.

    Arguments:
        svg: The svg to wrap into a data URL
    """
    if not isinstance(svg, str):
        msg = "Invalid type: %r"
        raise TypeError(msg, type(svg))
    return f"url('data:image/svg+xml;charset=utf-8,{ svg }')"


def clean_svg(text: str) -> str:
    """Strip off unwanted stuff from svg text which might be added by external libs.

    Removes xml headers and doctype declarations.

    Arguments:
        text: The text to cleanup / filter
    """
    text = re.sub(r"<\?xml version.*\?>\s*", "", text, flags=re.DOTALL)
    text = re.sub(r"<!DOCTYPE svg.*?>", "", text, flags=re.DOTALL)
    return text.strip()


def format_css_rule(dct: Mapping) -> str:
    """Format a nested dictionary as CSS rule.

    Mapping must be of shape {".a": {"b": "c"}}

    Arguments:
        dct: The mapping to convert to CSS text
    """
    data: dict[str, list] = {}

    def _parse(obj, selector: str = ""):
        for key, value in obj.items():
            if hasattr(value, "items"):
                rule = selector + " " + key
                data[rule] = []
                _parse(value, rule)

            else:
                prop = data[selector]
                prop.append(f"\t{key}: {value};\n")

    _parse(dct)
    string = ""
    for key, value in sorted(data.items()):
        if data[key]:
            string += key[1:] + " {\n" + "".join(value) + "}\n\n"
    return string


def format_xml(
    str_or_elem: str | Et.Element,
    indent: str | int = "  ",
    level: int = 0,
    method: Literal["xml", "html", "text", "c14n"] = "html",
    short_empty_elements: bool = True,
    add_declaration: bool = False,
) -> str:
    """(Pretty)print given XML.

    Arguments:
        str_or_elem: XML to prettyprint
        indent: Amount of spaces to use for indentation
        level: Initial indentation level
        method: Output method
        short_empty_elements: Whether empty elements should get printed in short form
                              (applies when mode is "xml")
        add_declaration: whether a XML declaration should be printed
                         (applies when mode is "xml")
    """
    if isinstance(str_or_elem, str):
        str_or_elem = Et.fromstring(str_or_elem)
    space = indent if isinstance(indent, str) else indent * " "
    Et.indent(str_or_elem, space=space, level=level)
    return Et.tostring(
        str_or_elem,
        encoding="unicode",
        method=method,
        xml_declaration=add_declaration,
        short_empty_elements=short_empty_elements,
    )


if __name__ == "__main__":
    print(format_js_map({"key": {"nested_key": "nested_value"}}))
