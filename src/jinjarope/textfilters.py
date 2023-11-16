from __future__ import annotations


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
