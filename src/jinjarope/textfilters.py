from __future__ import annotations

import os

from jinjarope import utils


def removesuffix(text: str, suffix: str) -> str:
    """Return given suffix from text.

    Arguments:
        text: The text to strip the suffix from
        suffix: The suffix to remove
    """
    return text.removesuffix(suffix)


def removeprefix(text: str, prefix: str) -> str:
    """Return given prefix from text.

    Arguments:
        text: The text to strip the prefix from
        prefix: The prefix to remove
    """
    return text.removeprefix(prefix)


def lstrip(text: str, chars: str | None = None) -> str:
    """Strip given chars from beginning of string.

    Arguments:
        text: The text to strip the chars from
        chars: The chars to remove
    """
    return text.lstrip(chars)


def rstrip(text: str, chars: str | None = None) -> str:
    """Strip given chars from end of string.

    Arguments:
        text: The text to strip the chars from
        chars: The chars to remove
    """
    return text.rstrip(chars)


def format_code(code: str, line_length: int = 100):
    """Format code to given line length using `black`.

    Arguments:
        code: The code to format
        line_length: Line length limit for formatted code
    """
    code = code.strip()
    if len(code) < line_length:
        return code
    formatter = utils._get_black_formatter()
    return formatter(code, line_length)


def slugify(text: str | os.PathLike) -> str:
    """Create a slug for given text.

    Returned text only contains alphanumerical and underscore.

    Arguments:
        text: text to get a slug for
    """
    import re

    text = str(text).lower()
    text = re.sub("[^0-9a-zA-Z_.]", "_", text)
    return re.sub("^[^0-9a-zA-Z_#]+", "", text)


if __name__ == "__main__":
    code = "def test(sth, fsjkdalfjksdalfjsadk, fjskldjfkdsljf, fsdkjlafjkdsafj): pass"
    result = format_code(code, line_length=50)
