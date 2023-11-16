from __future__ import annotations

import re

from typing import Literal


def md_link(
    text: str | None = None,
    link: str | None = None,
    tooltip: str | None = None,
) -> str:
    """Create a markdown link.

    If link is empty string or None, just the text will get returned.

    Arguments:
        text: Text to show for the link
        link: Target url
        tooltip: Optional tooltip
    """
    if not link:
        return text or ""
    tt = f" '{tooltip}'" if tooltip else ""
    return f"[{text or link}]({link}{tt})"


def extract_header_section(markdown: str, section_name: str) -> str | None:
    """Extract block with given header from markdown.

    Arguments:
        markdown: The markdown to extract a section from
        section_name: The header of the section to extract
    """
    header_pattern = re.compile(f"^(#+) {section_name}$", re.MULTILINE)
    header_match = header_pattern.search(markdown)
    if header_match is None:
        return None
    section_level = len(header_match[1])
    start_index = header_match.span()[1] + 1
    end_pattern = re.compile(f"^#{{1,{section_level}}} ", re.MULTILINE)
    end_match = end_pattern.search(markdown[start_index:])
    if end_match is None:
        return markdown[start_index:]
    end_index = end_match.span()[0]
    return markdown[start_index : end_index + start_index]


def md_escape(text: str, entity_type: str | None = None) -> str:
    """Helper function to escape markup.

    Args:
        text: The text.
        entity_type: For the entity types ``PRE``, ``CODE`` and the link
                     part of ``TEXT_LINKS``, only certain characters need to be escaped.
    """
    if entity_type in ["pre", "code"]:
        escape_chars = r"\`"
    elif entity_type == "text_link":
        escape_chars = r"\)"
    else:
        escape_chars = r"_*[]()~`>#+-=|{}.!"

    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


def md_style(
    text: str,
    *,
    size: int | None = None,
    bold: bool = False,
    italic: bool = False,
    code: bool = False,
    align: Literal["left", "right", "center"] | None = None,
) -> str:
    """Apply styling to given markdown.

    Arguments:
        text: Text to style
        size: Optional text size
        bold: Whether styled text should be bold
        italic: Whether styled text should be italic
        code: Whether styled text should styled as (inline) code
        align: Optional text alignment
    """
    if not text:
        return text or ""
    if size:
        text = f"<font size='{size}'>{text}</font>"
    if bold:
        text = f"**{text}**"
    if italic:
        text = f"*{text}*"
    if code:
        text = f"`{text}`"
    if align:
        text = f"<p style='text-align: {align};'>{text}</p>"
    return text


if __name__ == "__main__":
    print(md_link("a", "b"))
