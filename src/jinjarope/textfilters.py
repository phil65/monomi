from __future__ import annotations

from collections.abc import Callable
import inspect
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


def format_signature(
    fn: Callable,
    follow_wrapped: bool = True,
    eval_str: bool = True,
    remove_jinja_arg: bool = False,
) -> str:
    """Format signature of a callable.

    Arguments:
        fn: The callable to format the signature from
        follow_wrapped: Whether to unwrap the callable
        eval_str: Un-stringize annotations using eval
        remove_jinja_arg: If true, remove the first argument for pass_xyz decorated fns.
    """
    if eval_str:
        try:
            sig = inspect.signature(fn, follow_wrapped=follow_wrapped, eval_str=True)
        except (TypeError, NameError):
            sig = inspect.signature(fn, follow_wrapped=follow_wrapped, eval_str=False)
    else:
        sig = inspect.signature(fn, follow_wrapped=follow_wrapped, eval_str=False)
    if hasattr(fn, "jinja_pass_arg"):
        # for @pass_xyz decorated functions
        params = dict(sig._parameters)  # type: ignore[attr-defined]
        params.pop(next(iter(params)))
        sig._parameters = params  # type: ignore[attr-defined]
    return str(sig)


def format_filter_signature(
    fn: Callable,
    filter_name: str,
    follow_wrapped: bool = True,
    eval_str: bool = False,
) -> str:
    """Create a signature for a jinja filter based on filter name and callable.

    Outputs text in shape of
    "code: 'str' | test(line_length: 'int' = 100)"

    Arguments:
        fn: The callable to format the signature from
        filter_name: Name of the jinja filter
        follow_wrapped: Whether to unwrap the callable
        eval_str: Un-stringize annotations using eval
    """
    sig = inspect.signature(fn, follow_wrapped=follow_wrapped, eval_str=eval_str)
    params = dict(sig._parameters)  # type: ignore[attr-defined]
    if hasattr(fn, "jinja_pass_arg"):
        # for @pass_xyz decorated functions
        params.pop(next(iter(params)))
    first_val = params.pop(next(iter(params)))
    sig._parameters = params  # type: ignore[attr-defined]
    return f"{first_val} | {filter_name}{sig}"


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


def escape(text: str) -> str:
    """Escape text using Markupsafe library.

    Arguments:
        text: text to escape
    """
    import markupsafe

    return markupsafe.escape(text)


if __name__ == "__main__":
    code = "def test(sth, fsjkdalfjksdalfjsadk, fjskldjfkdsljf, fsdkjlafjkdsafj): pass"
    result = format_code(code, line_length=50)
