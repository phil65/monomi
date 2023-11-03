from __future__ import annotations

import mknodes as mk
import pytest

from mkdocs_mknodes import mkdocsconfig


@pytest.fixture(scope="session")
def config():
    return mkdocsconfig.Config()


@pytest.fixture(scope="session")
def mkdocs_mknodes_project():
    skin = mk.MaterialTheme()
    return mk.Project(skin, build_fn="mkdocs_mknodes.manual.root:build")
