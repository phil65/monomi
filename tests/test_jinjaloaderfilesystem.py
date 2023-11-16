from __future__ import annotations

import jinja2

from jinjarope import jinjaloaderfilesystem
import pytest


def test_jinja_loader_file_system():
    env = jinja2.Environment(
        loader=jinja2.DictLoader({"home.html": "Home", "about.html": "About"}),
    )
    fs = jinjaloaderfilesystem.JinjaLoaderFileSystem(env)

    assert fs.protocol == "jinja"
    assert fs.ls("") == [
        {"name": "about.html", "type": "file"},
        {"name": "home.html", "type": "file"},
    ]
    assert fs.cat("home.html") == b"Home"
    assert fs.cat("about.html") == b"About"
    with pytest.raises(FileNotFoundError):
        fs.cat("nonexistent.html")
