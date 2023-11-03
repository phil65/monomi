from __future__ import annotations

from collections.abc import Callable, Mapping
import pathlib
import types

from typing import Any

import fsspec
import fsspec.core
import jinja2

from jinjarope import utils


class LoaderMixin:
    """Loader mixin which allows to OR loaders into a choice loader."""

    ID: str
    loader: jinja2.BaseLoader
    list_templates: Callable

    def __or__(self, other: jinja2.BaseLoader):
        own = self.loaders if isinstance(self, jinja2.ChoiceLoader) else [self]  # type: ignore[list-item]
        others = other.loaders if isinstance(other, jinja2.ChoiceLoader) else [other]
        return ChoiceLoader([*own, *others])

    def __contains__(self, path):
        return pathlib.Path(path).as_posix() in self.list_templates()

    def __rtruediv__(self, path):
        return self.prefixed_with(path)

    def prefixed_with(self, prefix: str):
        """Return loader wrapped in a PrefixLoader instance with given prefix.

        Arguments:
            prefix: The prefix to use
        """
        return PrefixLoader({prefix: self})  # type: ignore[dict-item]


class PrefixLoader(LoaderMixin, jinja2.PrefixLoader):
    """A loader for prefixing other loaders."""

    ID = "prefix"

    def __repr__(self):
        return utils.get_repr(self, self.mapping)


class PackageLoader(LoaderMixin, jinja2.PackageLoader):
    """A loader for loading templates from a package."""

    ID = "package"

    def __init__(
        self,
        package: str | types.ModuleType,
        package_path: str | None = None,
        encoding: str = "utf-8",
    ) -> None:
        """Instanciate a PackageLoader.

        `package` can either be a `ModuleType` or a (dotted) module path.

        Arguments:
            package: The python package to create a loader for
            package_path: If given, use the given path as the root.
            encoding: The encoding to use for loading templates
        """
        if isinstance(package, types.ModuleType):
            package = package.__name__
        parts = package.split(".")
        path = "/".join(parts[1:])
        if package_path:
            path = (pathlib.Path(path) / package_path).as_posix()
        super().__init__(parts[0], path, encoding)

    def __repr__(self):
        return utils.get_repr(
            self,
            package_name=self.package_name,
            package_path=self.package_path,
        )


class FileSystemLoader(LoaderMixin, jinja2.FileSystemLoader):
    """A loader to load templates from the file system."""

    ID = "filesystem"

    def __repr__(self):
        return utils.get_repr(self, searchpath=self.searchpath)

    def __add__(self, other):
        if isinstance(other, jinja2.FileSystemLoader):
            paths = other.searchpath
        else:
            paths = [other]
        return FileSystemLoader([*self.searchpath, *paths])


class ChoiceLoader(LoaderMixin, jinja2.ChoiceLoader):
    """A loader which combines multiple other loaders."""

    ID = "choice"

    def __repr__(self):
        return utils.get_repr(self, loaders=self.loaders, _shorten=False)


class DictLoader(LoaderMixin, jinja2.DictLoader):
    """A loader to load static content from a path->template-str mapping."""

    ID = "dict"

    def __repr__(self):
        return utils.get_repr(self, mapping=self.mapping)

    def __add__(self, other):
        if isinstance(other, jinja2.DictLoader):
            mapping = self.mapping | other.mapping
        elif isinstance(other, dict):
            mapping = self.mapping | other
        return DictLoader(mapping)


class FsSpecProtocolPathLoader(LoaderMixin, jinja2.BaseLoader):
    """A jinja loader for fsspec filesystems.

    This loader allows to access templates from an fsspec protocol path,
    like "github://phil65:mknodes@main/README.md"

    Examples:
        ``` py
        loader = FsSpecProtocolPathLoader()
        env = Environment(loader=loader)
        env.get_template("github://phil65:mknodes@main/docs/icons.jinja").render()
        ```
    """

    ID = "fsspec_protocol_path"

    def get_source(
        self,
        environment: jinja2.Environment | None,
        template: str,
    ) -> tuple[str, str, Callable[[], bool] | None]:
        src = utils.fsspec_get(template)
        path = pathlib.Path(template).as_posix()
        return src, path, lambda: True

    def list_templates(self) -> list[str]:
        return []

    def __contains__(self, path: str):
        try:
            self.get_source(None, path)
        except FileNotFoundError:
            return False
        else:
            return True

    def __repr__(self):
        return utils.get_repr(self)


class FsSpecFileSystemLoader(LoaderMixin, jinja2.BaseLoader):
    """A jinja loader for fsspec filesystems.

    This loader allows to access templates from an fsspec filesystem.

    Template paths must be relative to the filesystem root.
    In order to access templates via protocol path, see `FsSpecProtocolPathLoader`.

    Examples:
        ``` py
        # protocol path
        loader = FsSpecFileSystemLoader("dir::github://phil65:mknodes@main/docs")
        env = Environment(loader=loader)
        env.get_template("icons.jinja").render()

        # protocol and storage options
        loader = FsSpecFileSystemLoader("github", org="phil65", repo="mknodes")
        env = Environment(loader=loader)
        env.get_template("docs/icons.jinja").render()

        # fsspec filesystem
        fs = fsspec.filesystem("github", org="phil65", repo="mknodes")
        loader = FsSpecFileSystemLoader(fs)
        env = Environment(loader=loader)
        env.get_template("docs/icons.jinja").render()
        ```

    """

    ID = "fsspec"

    def __init__(self, fs: fsspec.AbstractFileSystem | str, **kwargs: Any):
        """Constructor.

        Arguments:
            fs: Either a protocol path string or an fsspec filesystem instance.
                Also supports "::dir" prefix to set the root path.
            kwargs: Optional storage options for the filesystem.
        """
        super().__init__()
        match fs:
            case str() if "://" in fs:
                self.fs, self.path = fsspec.core.url_to_fs(fs, **kwargs)
            case str():
                self.fs, self.path = fsspec.filesystem(fs, **kwargs), ""
            case _:
                self.fs, self.path = fs, ""
        self.storage_options = kwargs

    def __repr__(self):
        return utils.get_repr(self, fs=self.fs.protocol, **self.storage_options)

    def list_templates(self) -> list[str]:
        return self.fs.ls(self.fs.root_marker)

    def get_source(
        self,
        environment: jinja2.Environment,
        template: str,
    ) -> tuple[str, str, Callable[[], bool] | None]:
        with self.fs.open(template) as file:
            src = file.read().decode()

        path = pathlib.Path(template).as_posix()
        return src, path, lambda: True


def flatten_dict(dct: Mapping, sep: str = "/", parent_key: str = "") -> Mapping:
    items: list[tuple[str, str]] = []
    for k, v in dct.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, Mapping):
            items.extend(flatten_dict(v, parent_key=new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class NestedDictLoader(LoaderMixin, jinja2.BaseLoader):
    """A jinja loader for loading templates from nested dicts.

    This loader allows to access templates from nested dicts.
    Can be used to load templates defined with markup like TOML.

    Examples:
        ``` toml
        [example]
        template = "{{ something }}"
        ```

        content = tomllib.load(toml_file)
        loader = NestedDictLoader(content)
        env = Environment(loader=loader)
        env.get_template("example/template")
    """

    ID = "nested_dict"

    def __init__(self, mapping: Mapping):
        """Constructor.

        Arguments:
            mapping: A nested dict containing templates
        """
        super().__init__()
        self._data = mapping

    def __repr__(self):
        return utils.get_repr(self, mapping=self._data)

    def list_templates(self) -> list[str]:
        return list(flatten_dict(self._data).keys())

    def get_source(
        self,
        environment: jinja2.Environment,
        template: str,
    ) -> tuple[str, str, Callable[[], bool] | None]:
        data: Any = self._data
        for part in template.split("/"):
            data = data[part]
        return data, None, lambda: True  # type: ignore[return-value]


def from_json(dct_or_list) -> jinja2.BaseLoader | None:
    if not dct_or_list:
        return None
    loaders = []
    ls = dct_or_list if isinstance(dct_or_list, list) else [dct_or_list]
    for item in ls:
        match item:
            case jinja2.BaseLoader():
                loaders.append(item)
            case str() if "://" in item:
                loaders.append(FsSpecFileSystemLoader(item))
            case str():
                loaders.append(FileSystemLoader(item))
            case types.ModuleType():
                loaders.append(PackageLoader(item))
            case dict():
                for kls in jinja2.BaseLoader.__subclasses__():
                    if not issubclass(kls, LoaderMixin):
                        continue
                    dct_copy = item.copy()
                    if dct_copy.pop("type") == kls.ID:  # type: ignore[attr-defined]
                        path = dct_copy.pop("path")
                        instance = kls(path, **dct_copy)  # type: ignore[call-arg]
                        loaders.append(instance)
    match len(loaders):
        case 1:
            return loaders[0]
        case 0:
            return None
        case _:
            return ChoiceLoader(loaders)


LOADERS = dict(
    fsspec=FsSpecFileSystemLoader,
    filesystem=FileSystemLoader,
    package=PackageLoader,
    dictionary=DictLoader,
)


if __name__ == "__main__":
    from jinjarope import Environment

    loader = FsSpecFileSystemLoader("dir::github://phil65:mknodes@main/docs")
    env = Environment()
    env.loader = loader
    template = env.get_template("icons.jinja")
    print(template.render())
    loader = FsSpecProtocolPathLoader()
    result = loader.get_source(env, "github://phil65:mknodes@main/README.md")
    print(repr(loader))
