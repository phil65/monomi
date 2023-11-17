# jinjarope

[![PyPI License](https://img.shields.io/pypi/l/jinjarope.svg)](https://pypi.org/project/jinjarope/)
[![Package status](https://img.shields.io/pypi/status/jinjarope.svg)](https://pypi.org/project/jinjarope/)
[![Daily downloads](https://img.shields.io/pypi/dd/jinjarope.svg)](https://pypi.org/project/jinjarope/)
[![Weekly downloads](https://img.shields.io/pypi/dw/jinjarope.svg)](https://pypi.org/project/jinjarope/)
[![Monthly downloads](https://img.shields.io/pypi/dm/jinjarope.svg)](https://pypi.org/project/jinjarope/)
[![Distribution format](https://img.shields.io/pypi/format/jinjarope.svg)](https://pypi.org/project/jinjarope/)
[![Wheel availability](https://img.shields.io/pypi/wheel/jinjarope.svg)](https://pypi.org/project/jinjarope/)
[![Python version](https://img.shields.io/pypi/pyversions/jinjarope.svg)](https://pypi.org/project/jinjarope/)
[![Implementation](https://img.shields.io/pypi/implementation/jinjarope.svg)](https://pypi.org/project/jinjarope/)
[![Releases](https://img.shields.io/github/downloads/phil65/jinjarope/total.svg)](https://github.com/phil65/jinjarope/releases)
[![Github Contributors](https://img.shields.io/github/contributors/phil65/jinjarope)](https://github.com/phil65/jinjarope/graphs/contributors)
[![Github Discussions](https://img.shields.io/github/discussions/phil65/jinjarope)](https://github.com/phil65/jinjarope/discussions)
[![Github Forks](https://img.shields.io/github/forks/phil65/jinjarope)](https://github.com/phil65/jinjarope/forks)
[![Github Issues](https://img.shields.io/github/issues/phil65/jinjarope)](https://github.com/phil65/jinjarope/issues)
[![Github Issues](https://img.shields.io/github/issues-pr/phil65/jinjarope)](https://github.com/phil65/jinjarope/pulls)
[![Github Watchers](https://img.shields.io/github/watchers/phil65/jinjarope)](https://github.com/phil65/jinjarope/watchers)
[![Github Stars](https://img.shields.io/github/stars/phil65/jinjarope)](https://github.com/phil65/jinjarope/stars)
[![Github Repository size](https://img.shields.io/github/repo-size/phil65/jinjarope)](https://github.com/phil65/jinjarope)
[![Github last commit](https://img.shields.io/github/last-commit/phil65/jinjarope)](https://github.com/phil65/jinjarope/commits)
[![Github release date](https://img.shields.io/github/release-date/phil65/jinjarope)](https://github.com/phil65/jinjarope/releases)
[![Github language count](https://img.shields.io/github/languages/count/phil65/jinjarope)](https://github.com/phil65/jinjarope)
[![Github commits this week](https://img.shields.io/github/commit-activity/w/phil65/jinjarope)](https://github.com/phil65/jinjarope)
[![Github commits this month](https://img.shields.io/github/commit-activity/m/phil65/jinjarope)](https://github.com/phil65/jinjarope)
[![Github commits this year](https://img.shields.io/github/commit-activity/y/phil65/jinjarope)](https://github.com/phil65/jinjarope)
[![Package status](https://codecov.io/gh/phil65/jinjarope/branch/main/graph/badge.svg)](https://codecov.io/gh/phil65/jinjarope/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyUp](https://pyup.io/repos/github/phil65/jinjarope/shield.svg)](https://pyup.io/repos/github/phil65/jinjarope/)

[Read the documentation!](https://phil65.github.io/jinjarope/)

## How to install

### pip

The latest released version is available at the [Python package index](https://pypi.org/project/mknodes).

``` py
pip install jinjarope
```


## Quick guide

Jinjarope contains a range of Jinja2 loaders (including fsspec-based ones) as well as a `jinja2.Environment` subclass with added functionality.

For debugging purposes, an FsSpec filesystem implementation for jinja2 loaders is also included.


### FsSpecFileSystemLoader

This loader can be used like a FileSystemLoader, but also works on any fsspec-supported
remote path.
Using the `dir::` prefix, any folder can be set as root.

``` py
# protocol path
loader = jinjarope.FsSpecFileSystemLoader("dir::github://phil65:jinjarope@main/tests/testresources")
env = jinjarope.Environment(loader=loader)
env.get_template("testfile.jinja").render()

# protocol and storage options
loader = jinjarope.FsSpecFileSystemLoader("github", org="phil65", repo="jinjarope")
env = jinjarope.Environment(loader=loader)
env.get_template("README.md").render()

# fsspec filesystem
fs = fsspec.filesystem("github", org="phil65", repo="jinjarope")
loader = jinjarope.FsSpecFileSystemLoader(fs)
env = jinjarope.Environment(loader=loader)
env.get_template("README.md").render()
```


### FsSpecProtocolPathLoader

This loader accepts any FsSpec protocol path to be used directly.
A complete protocol URL to the template file is required.

``` py
loader = jinjarope.FsSpecProtocolPathLoader()
env = jinjarope.Environment(loader=loader)
env.get_template("github://phil65:jinjarope@main/tests/testresources/testfile.jinja").render()
```


### NestedDictLoader

``` toml
[example]
template = "{{ something }}"
```
``` py
content = tomllib.load(toml_file)
loader = jinjarope.NestedDictLoader(content)
env = jinjarope.Environment(loader=loader)
env.get_template("example/template")
```


### General loader information

**jinjarope** also contains subclasses for all default **jinja2** loaders. These loaders
have implementations for some magic methods (`__eq__`, `__hash__`, `__repr__`, , `__getitem__`).

``` py
loader = jinjarope.FileSystemLoader(...)
template_source = loader["path/to/template.jinja"]
```

The loaders can also get ORed to return a ChoiceLoader.

``` py
choice_loader = jinjarope.FileSystemLoader(..) | jinjarope.PackageLoader(...)
```

Prefix loaders can get created using pathlib-style string concatenations

``` py
prefix_loader = "path_prefix" / jinjarope.FileSystemLoader(...)
```

### Additional filters / tests

Check out the documentation for a list of built-in filters and tests!
