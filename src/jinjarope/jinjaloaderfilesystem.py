"""Filesystem implementation for jinja environment templates."""

from __future__ import annotations

import logging
from typing import Any, Literal

import fsspec
from fsspec.implementations import memory
import jinja2
from upath import UPath


logger = logging.getLogger(__name__)


class JinjaLoaderFileSystem(fsspec.AbstractFileSystem):
    """A FsSpec Filesystem implementation for jinja environment templates.

    This virtual file system allows browsing and accessing all available templates of an
    environment by utilizing `BaseLoader.list_templates` and `BaseLoader.get_source`.
    """

    protocol = "jinja"

    def __init__(self, env: jinja2.Environment) -> None:
        """Initialize a JinjaLoader filesystem.

        Args:
            env: The environment of the loaders to get a filesystem for.
        """
        super().__init__()
        self.env = env

    def ls(
        self, path: str, detail: bool = True, **kwargs: Any
    ) -> list[dict[str, str]] | list[str]:
        """List contents of path.

        Args:
            path: The path to list
            detail: If True, return a list of dictionaries, else return a list of paths
            **kwargs: Additional arguments (unused)

        Returns:
            List of paths or file details

        Raises:
            FileNotFoundError: If path doesn't exist or env has no loader
        """
        if not self.env.loader:
            msg = "Environment has no loader"
            raise FileNotFoundError(msg)

        templates = self.env.loader.list_templates()
        clean_path = UPath(path).as_posix().strip("/")

        if clean_path in {"", "/", "."}:
            return self._list_root(templates, detail)
        return self._list_subdirectory(templates, clean_path, detail)

    def _list_root(
        self, templates: list[str], detail: bool
    ) -> list[dict[str, str]] | list[str]:
        """List contents of root directory.

        Args:
            templates: List of all template paths
            detail: If True, return detailed information

        Returns:
            List of paths or file details
        """
        root_files = [path for path in templates if "/" not in path]
        root_dirs = {
            path.split("/")[0]
            for path in templates
            if "/" in path and path not in root_files
        }

        if detail:
            file_entries = [{"name": path, "type": "file"} for path in root_files]
            dir_entries = [{"name": path, "type": "directory"} for path in root_dirs]
            return dir_entries + file_entries
        return list(root_dirs) + root_files

    def _list_subdirectory(
        self, templates: list[str], path: str, detail: bool
    ) -> list[dict[str, str]] | list[str]:
        """List contents of a subdirectory.

        Args:
            templates: List of all template paths
            path: Directory path to list
            detail: If True, return detailed information

        Returns:
            List of paths or file details

        Raises:
            FileNotFoundError: If directory doesn't exist
        """
        items = [
            UPath(template).name
            for template in templates
            if template.rsplit("/", 1)[0] == path
        ]

        if not items:
            msg = f"Directory not found: {path}"
            raise FileNotFoundError(msg)

        if detail:
            return [
                {
                    "name": item,
                    "type": "file" if "." in item else "directory",
                }
                for item in items
            ]
        return items

    def _open(
        self,
        path: str,
        mode: Literal["rb", "wb", "ab"] = "rb",
        block_size: int | None = None,
        autocommit: bool = True,
        cache_options: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> memory.MemoryFile:
        """Open a file.

        Args:
            path: Path to file
            mode: Mode to open file
            block_size: Size of blocks to read/write
            autocommit: Whether to commit automatically
            cache_options: Cache options
            **kwargs: Additional arguments

        Returns:
            Opened file object

        Raises:
            FileNotFoundError: If template not found or env has no loader
        """
        if not self.env.loader:
            msg = "Environment has no loader"
            raise FileNotFoundError(msg)

        try:
            source, _, _ = self.env.loader.get_source(self.env, path)
            return memory.MemoryFile(fs=self, path=path, data=source.encode())
        except jinja2.TemplateNotFound as exc:
            msg = f"Template not found: {path}"
            raise FileNotFoundError(msg) from exc


if __name__ == "__main__":
    from jinjarope import loaders

    fsspec.register_implementation("jinja", JinjaLoaderFileSystem)
    template_env = jinja2.Environment(loader=loaders.PackageLoader("jinjarope"))
    filesystem = fsspec.filesystem("jinja", env=template_env)
    path = UPath("jinja://htmlfilters.py", env=template_env)
    print(path.read_text())
