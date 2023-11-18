from __future__ import annotations

import jinja2

from jinjarope import environment, fsspecloaders
import pytest


def test_fsspec_protocol_loader():
    env = environment.Environment()
    env.loader = fsspecloaders.FsSpecProtocolPathLoader()
    assert env.get_template("file://tests/testresources/testfile.jinja").render()
    assert "file://tests/testresources/testfile.jinja" in env.loader
    assert "file://not_existing.jinja" not in env.loader
    with pytest.raises(jinja2.TemplateNotFound):
        env.get_template("file://tests/testresources/not-existing.jinja")


def test_fsspec_filesystem_loader():
    env = environment.Environment()
    env.loader = fsspecloaders.FsSpecFileSystemLoader("file")
    assert env.get_template("tests/testresources/testfile.jinja").render()
    env.loader = fsspecloaders.FsSpecFileSystemLoader("file://")
    assert env.get_template("tests/testresources/testfile.jinja").render()
    with pytest.raises(jinja2.TemplateNotFound):
        env.get_template("tests/testresources/not-existing.jinja")


def test_fsspec_filesystem_loader_with_dir_prefix():
    env = environment.Environment()
    env.loader = fsspecloaders.FsSpecFileSystemLoader("dir::file://tests/testresources")
    assert env.get_template("testfile.jinja").render()
    with pytest.raises(jinja2.TemplateNotFound):
        env.get_template("not-existing.jinja")
