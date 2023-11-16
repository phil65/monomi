from __future__ import annotations

import io
import logging
import pathlib

import fsspec
import jinja2


logger = logging.getLogger(__name__)


class JinjaLoaderFileSystem(fsspec.AbstractFileSystem):
    """A **FsSpec** Filesystem implementation for jinja environment templates.

    This virtual file system allows to browse and access all available templates of an
    environment by utilizing `BaseLoader.list_templates` and `BaseLoader.get_source`.
    """

    protocol = "jinja"

    def __init__(self, env: jinja2.Environment):
        """Instanciate a JinjaLoader filesystem.

        Arguments:
            env: The environment of the loaders to get a filesystem for.
        """
        super().__init__()
        self.env = env

    def ls(self, path: str, detail: bool = True, **kwargs) -> list:
        """Implementation for AbstractFileSystem."""
        if not self.env.loader:
            raise FileNotFoundError(path)
        paths = self.env.loader.list_templates()
        path = pathlib.Path(path).as_posix().strip("/")
        if path in {"", "/", "."}:
            """Root, return all."""
            if detail:
                files = [{"name": p, "type": "file"} for p in paths if "/" not in p]
                dirs = [
                    {"name": p.split("/")[0], "type": "directory"}
                    for p in paths
                    if p.count("/") >= 1 and p not in files
                ]
                dirs = [i for n, i in enumerate(dirs) if i not in dirs[n + 1 :]]
                return dirs + files
            files = [p for p in paths if "/" not in p]
            dirs = [
                p.split("/")[0] for p in paths if p.count("/") >= 1 and p not in files
            ]
            return list(set(dirs)) + files
        if detail:
            items = [
                {
                    "name": pathlib.Path(i).name,
                    "type": "file" if "." in pathlib.Path(i).name else "directory",
                }
                for i in paths
                if i.rsplit("/", 1)[0] == path
            ]
        else:
            items = [pathlib.Path(i).name for i in paths if i.rsplit("/", 1)[0] == path]
        if not items:
            raise FileNotFoundError(path)
        return items

    def _open(self, path: str, mode="rb", **kwargs) -> io.BytesIO:
        if not self.env.loader:
            msg = "Environment has no loader set"
            raise FileNotFoundError(msg)
        try:
            src, _filename, _uptodate = self.env.loader.get_source(self.env, path)
            return io.BytesIO(src.encode())
        except jinja2.TemplateNotFound as e:
            raise FileNotFoundError(path) from e


if __name__ == "__main__":
    from jinjarope import loaders

    fsspec.register_implementation("jinja", JinjaLoaderFileSystem)
    env = jinja2.Environment(loader=loaders.PackageLoader("jinjarope"))
    fs = fsspec.filesystem("jinja", env=env)
    print(fs.ls(""))
