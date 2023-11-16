from __future__ import annotations

import jinja2

from jinjarope import jinjaloaderfilesystem
import pytest


dct = {"home.html": "Home", "about.html": "About", "subfolder/sub.html": "Sub"}


def test_jinja_loader_file_system():
    env = jinja2.Environment(
        loader=jinja2.DictLoader(dct),
    )
    fs = jinjaloaderfilesystem.JinjaLoaderFileSystem(env)

    assert fs.protocol == "jinja"
    assert fs.ls("") == [
        {"name": "subfolder", "type": "directory"},
        {"name": "about.html", "type": "file"},
        {"name": "home.html", "type": "file"},
    ]
    assert fs.ls("", detail=False) == ["subfolder", "about.html", "home.html"]
    assert fs.ls("subfolder/", detail=False) == ["sub.html"]
    assert fs.ls("subfolder/", detail=True) == [{"name": "sub.html", "type": "file"}]
    assert fs.cat("home.html") == b"Home"
    assert fs.cat("about.html") == b"About"
    with pytest.raises(FileNotFoundError):
        fs.cat("nonexistent.html")
    with pytest.raises(FileNotFoundError):
        fs.ls("not-existing-dir")
    fs.env = jinja2.Environment()
    with pytest.raises(FileNotFoundError):
        fs.ls("no-loader-set")
    with pytest.raises(FileNotFoundError):
        fs.open("no-loader-set")
