``` py title='__main__.create_github_index_md' linenums="86" hl_lines="3"
def create_github_index_md() -> mk.MkPage:
    page = mk.MkPage("Github index")
    page += mk.MkCode.for_object(create_github_index_md)
    page += mk.MkHeader("MkNodes", level=1)
    page += mk.MkHeader("Don't write docs. Code them.", level=4)
    page += mk.MkShields()
    page += mk.MkLink(DOC_URL, "Read the completely coded documentation!")
    page += mk.MkInstallGuide(header="How to install")
    page += mk.MkHeader("All the nodes!")
    page += mk.MkClassDiagram(mk.MkNode, mode="subclasses", direction="LR")
    return page

```

# MkNodes (Mkdocs Plugin)

#### Don't write docs. Code them.

[![PyPI License](https://img.shields.io/pypi/l/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Package status](https://img.shields.io/pypi/status/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Daily downloads](https://img.shields.io/pypi/dd/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Weekly downloads](https://img.shields.io/pypi/dw/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Monthly downloads](https://img.shields.io/pypi/dm/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Distribution format](https://img.shields.io/pypi/format/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Wheel availability](https://img.shields.io/pypi/wheel/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Python version](https://img.shields.io/pypi/pyversions/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Implementation](https://img.shields.io/pypi/implementation/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Releases](https://img.shields.io/github/downloads/phil65/mkdocs_mknodes/total.svg)](https://github.com/phil65/monomi/releases)
[![Github Contributors](https://img.shields.io/github/contributors/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/graphs/contributors)
[![Github Discussions](https://img.shields.io/github/discussions/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/discussions)
[![Github Forks](https://img.shields.io/github/forks/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/forks)
[![Github Issues](https://img.shields.io/github/issues/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/issues)
[![Github Issues](https://img.shields.io/github/issues-pr/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/pulls)
[![Github Watchers](https://img.shields.io/github/watchers/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/watchers)
[![Github Stars](https://img.shields.io/github/stars/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/stars)
[![Github Repository size](https://img.shields.io/github/repo-size/phil65/mkdocs_mknodes)](https://github.com/phil65/mkdocs_mknodes)
[![Github last commit](https://img.shields.io/github/last-commit/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/commits)
[![Github release date](https://img.shields.io/github/release-date/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/releases)
[![Github language count](https://img.shields.io/github/languages/count/phil65/mkdocs_mknodes)](https://github.com/phil65/mkdocs_mknodes)
[![Github commits this week](https://img.shields.io/github/commit-activity/w/phil65/mkdocs_mknodes)](https://github.com/phil65/mkdocs_mknodes)
[![Github commits this month](https://img.shields.io/github/commit-activity/m/phil65/mkdocs_mknodes)](https://github.com/phil65/mkdocs_mknodes)
[![Github commits this year](https://img.shields.io/github/commit-activity/y/phil65/mkdocs_mknodes)](https://github.com/phil65/mkdocs_mknodes)
[![Package status](https://codecov.io/gh/phil65/mkdocs_mknodes/branch/main/graph/badge.svg)](https://codecov.io/gh/phil65/mkdocs_mknodes/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyUp](https://pyup.io/repos/github/phil65/mkdocs_mknodes/shield.svg)](https://pyup.io/repos/github/phil65/mkdocs_mknodes/)

[Read the completely coded documentation!](https://phil65.github.io/mkdocs-mknodes/)

## How to install

### pip

The latest released version is available at the [Python package index](https://pypi.org/project/mknodes).

``` py
pip install mkdocs-mknodes
```
