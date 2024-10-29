from __future__ import annotations

from typing import Literal

from jinjarope import icons


Rotation = Literal["90", "180", "270", 90, 180, 270, "-90", 1, 2, 3]
Flip = Literal["horizontal", "vertical", "horizontal,vertical"]


def get_favicon(
    url: str,
    provider: Literal[
        "google", "duckduckgo", "iconhorse", "yandex", "favicon_io", "favicon_ninja"
    ] = "duckduckgo",
    size: int = 32,
):
    """Return a favicon URL for the given URL.

    Arguments:
        url: The URL to get the favicon for.
        provider: The provider to use for the favicon.
        size: Size of the favicon in pixels (not supported by all providers)
    """
    from urllib.parse import urlparse

    # Parse the URL to get the domain
    domain = urlparse(url).netloc or url

    match provider:
        case "google":
            return f"https://www.google.com/s2/favicons?domain={domain}&sz={size}"
        case "duckduckgo":
            return f"https://icons.duckduckgo.com/ip3/{domain}.ico"
        case "iconhorse":
            return f"https://icon.horse/icon/{domain}?size={size}"
        case "yandex":
            # Yandex supports sizes: 16, 32, 76, 120, 180, 192, 256
            valid_sizes = [16, 32, 76, 120, 180, 192, 256]
            closest_size = min(valid_sizes, key=lambda x: abs(x - size))
            return f"https://favicon.yandex.net/favicon/{domain}?size={closest_size}"
        case "favicon_io":
            return f"https://favicon.io/favicon/{domain}"
        case "favicon_ninja":
            return f"https://favicon.ninja/icon?url={domain}&size={size}"
        case _:
            msg = f"Invalid provider: {provider}"
            raise ValueError(msg)


def get_icon_svg(
    icon: str,
    color: str | None = None,
    height: str | int | None = None,
    width: str | int | None = None,
    flip: Flip | None = None,
    rotate: Rotation | None = None,
    box: bool | None = None,
) -> str:
    """Return svg for given pyconify icon key.

    Key should look like "mdi:file"
    For compatibility, this method also supports compatibility for
    emoji-slugs (":material-file:") as well as material-paths ("material/file")

    If no icon group is supplied as part of the string, mdi is assumed as group.

    When passing a string with "|" delimiters, the returned string will contain multiple
    icons.

    Arguments:
        icon: Pyconify icon name
        color: Icon color. Replaces currentColor with specific color, resulting in icon
               with hardcoded palette.
        height: Icon height. If only one dimension is specified, such as height, other
                dimension will be automatically set to match it.
        width: Icon width. If only one dimension is specified, such as height, other
               dimension will be automatically set to match it.
        flip: Flip icon.
        rotate: Rotate icon. If an integer is provided, it is assumed to be in degrees.
        box: Adds an empty rectangle to SVG that matches the icon's viewBox. It is needed
            when importing SVG to various UI design tools that ignore viewBox. Those
            tools, such as Sketch, create layer groups that automatically resize to fit
            content. Icons usually have empty pixels around icon, so such software crops
            those empty pixels and icon's group ends up being smaller than actual icon,
            making it harder to align it in design.

    Example:
        get_icon_svg("file")  # implicit mdi group
        get_icon_svg("mdi:file")  # pyconify key
        get_icon_svg("material/file")  # Material-style path
        get_icon_svg(":material-file:")  # material-style emoji slug
        get_icon_svg("mdi:file|:material-file:")  # returns a string with two svgs
    """
    label = ""
    for splitted in icon.split("|"):
        key = get_pyconify_key(splitted)
        import pyconify

        label += pyconify.svg(
            key,
            color=color,
            height=height,
            width=width,
            flip=flip,
            rotate=rotate,
            box=box,
        ).decode()
    return label


def get_pyconify_key(icon: str) -> str:
    """Convert given string to a pyconify key.

    Converts the keys from MkDocs-Material ("material/sth" or ":material-sth:")
    to their pyconify equivalent.

    Arguments:
        icon: The string which should be converted to a pyconify key.
    """
    for k, v in icons.PYCONIFY_TO_PREFIXES.items():
        path = f"{v.replace('-', '/')}/"
        icon = icon.replace(path, f"{k}:")
        icon = icon.replace(f":{v}-", f"{k}:")
    icon = icon.strip(":")
    mapping = {k: v[0] for k, v in icons._get_collection_map().items()}
    for prefix in mapping:
        if icon.startswith(f"{prefix}-"):
            icon = icon.replace(f"{prefix}-", f"{prefix}:")
            break
    if (count := icon.count(":")) > 1:
        icon = icon.replace(":", "-", count - 1)
    if ":" not in icon:
        icon = f"mdi:{icon}"
    return icon
