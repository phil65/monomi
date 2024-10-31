from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
import re
from re import Pattern
import stat
from typing import TYPE_CHECKING, Any

from jinja2 import filters
import upath

from jinjarope import iconfilters, textfilters


if TYPE_CHECKING:
    import os
    import pathlib


class SortCriteria(Enum):
    """Enumeration for different sorting criteria."""

    NAME = auto()
    SIZE = auto()
    DATE = auto()
    EXTENSION = auto()


@dataclass
class TreeOptions:
    """Configuration options for directory tree printing."""

    show_hidden: bool = False
    show_size: bool = True
    show_date: bool = False
    show_permissions: bool = False
    show_icons: bool = True
    max_depth: int | None = None
    include_pattern: Pattern[str] | None = None
    exclude_pattern: Pattern[str] | None = None
    allowed_extensions: set[str] | None = None
    hide_empty: bool = True
    sort_criteria: SortCriteria = SortCriteria.NAME
    reverse_sort: bool = False
    date_format: str = "%Y-%m-%d %H:%M:%S"


def _get_path_info(path: pathlib.Path) -> dict[str, Any]:
    """Get all relevant information about a path."""
    try:
        stats = path.stat()
        return {
            "size": stats.st_size,
            "mtime": stats.st_mtime,
            "mode": stats.st_mode,
            "is_dir": path.is_dir(),
            "name": path.name,
            "extension": path.suffix.lower(),
        }
    except OSError:
        return {
            "size": 0,
            "mtime": 0,
            "mode": 0,
            "is_dir": path.is_dir(),
            "name": path.name,
            "extension": path.suffix.lower(),
        }


class DirectoryTree:
    """A class to generate and print directory tree structure."""

    PIPE = "┃   "
    ELBOW = "┗━━ "
    TEE = "┣━━ "
    DIRECTORY = "📂"

    def __init__(
        self,
        root_path: str | os.PathLike[str],
        options: TreeOptions | None = None,
    ) -> None:
        self.root_path = upath.UPath(root_path)
        self.options = options or TreeOptions()

    def _get_sort_key(self, path: pathlib.Path) -> tuple[bool, Any]:
        """Generate sort key based on current sort criteria."""
        info = _get_path_info(path)
        criteria_keys = {
            SortCriteria.NAME: lambda: (info["name"].lower(),),
            SortCriteria.SIZE: lambda: (info["size"],),
            SortCriteria.DATE: lambda: (info["mtime"],),
            SortCriteria.EXTENSION: lambda: (info["extension"], info["name"].lower()),
        }
        # Always sort directories first within each category
        return not path.is_dir(), criteria_keys[self.options.sort_criteria]()

    def _should_include(self, path: pathlib.Path) -> bool:
        """Check if path should be included based on filters."""
        name = path.name

        if not self.options.show_hidden and name.startswith("."):
            return False

        if self.options.include_pattern and not self.options.include_pattern.match(name):
            return False

        if self.options.exclude_pattern and self.options.exclude_pattern.match(name):
            return False

        return not (
            self.options.allowed_extensions
            and (
                path.is_file()
                and path.suffix.lower() not in self.options.allowed_extensions
            )
        )

    def _is_directory_empty_after_filters(
        self,
        directory: pathlib.Path,
        depth: int = 0,
    ) -> bool:
        """Recursively check if directory is empty after applying all filters.

        Returns True if directory has no visible contents after filtering.
        """
        if self.options.max_depth is not None and depth > self.options.max_depth:
            return True

        try:
            # Get all paths and apply filters
            paths = [p for p in directory.iterdir() if self._should_include(p)]

            # If no paths remain after filtering, directory is considered empty
            if not paths:
                return True

            # For directories, recursively check if they're empty
            for path in paths:
                if path.is_dir():
                    # If a directory is not empty, this directory is not empty
                    if not self._is_directory_empty_after_filters(path, depth + 1):
                        return False
                else:
                    # If we find any visible file, directory is not empty
                    return False
            else:
                # If we only found empty directories, this directory is empty
                return True

        except (PermissionError, OSError):
            # Treat inaccessible directories as empty
            return True

    def _get_tree_entries(
        self, directory: pathlib.Path, prefix: str = "", depth: int = 0
    ) -> list[tuple[str, pathlib.Path, bool]]:
        """Generate tree entries with proper formatting."""
        entries: list[tuple[str, pathlib.Path, bool]] = []

        if self.options.max_depth is not None and depth > self.options.max_depth:
            return entries

        try:
            # Get all paths and apply sorting
            paths = sorted(
                directory.iterdir(),
                key=self._get_sort_key,
                reverse=self.options.reverse_sort,
            )
        except (PermissionError, OSError) as e:
            print(f"Error accessing {directory}: {e}")
            return entries

        # Filter paths and check if they're empty (if directories)
        visible_paths: list[pathlib.Path] = []
        for path in paths:
            if not self._should_include(path):
                continue

            if (
                path.is_dir()
                and self.options.hide_empty
                and self._is_directory_empty_after_filters(path, depth + 1)
            ):
                continue
            visible_paths.append(path)

        # Process visible paths
        for i, path in enumerate(visible_paths):
            is_last = i == len(visible_paths) - 1
            connector = self.ELBOW if is_last else self.TEE

            entries.append((f"{prefix}{connector}", path, is_last))

            if path.is_dir():
                new_prefix = f"{prefix}{self.PIPE}" if not is_last else f"{prefix}    "
                entries.extend(self._get_tree_entries(path, new_prefix, depth + 1))

        return entries

    def print_tree(self) -> None:
        """Print the directory tree structure."""
        if not self.root_path.exists():
            msg = f"Path does not exist: {self.root_path}"
            raise FileNotFoundError(msg)

        # Check if root directory is empty after filtering
        if self.options.hide_empty and self._is_directory_empty_after_filters(
            self.root_path
        ):
            icon = self.DIRECTORY if self.options.show_icons else ""
            print(f"{icon} {self.root_path.name} (empty)")
            return

        root_icon = self.DIRECTORY if self.options.show_icons else ""
        print(f"{root_icon} {self.root_path.name}")

        for prefix, path, _is_last in self._get_tree_entries(self.root_path):
            info = _get_path_info(path)

            # Prepare icon
            icon = ""
            if self.options.show_icons:
                icon = (
                    self.DIRECTORY
                    if info["is_dir"]
                    else iconfilters.get_path_ascii_icon(path)
                )

            # Prepare additional information
            details: list[str] = []

            if self.options.show_size and not info["is_dir"]:
                details.append(f"{filters.do_filesizeformat(info['size'])}")

            if self.options.show_date:
                s = textfilters.format_timestamp(info["mtime"], self.options.date_format)
                details.append(s)
            if self.options.show_permissions:
                permissions = stat.filemode(info["mode"])
                details.append(permissions)

            details_str = f" ({', '.join(details)})" if details else ""

            print(f"{prefix}{icon} {path.name}{details_str}")


def main() -> None:
    # Example usage with various options
    options = TreeOptions(
        show_hidden=False,
        show_size=True,
        max_depth=4,
        # include_pattern=re.compile(r".*\.py$|.*\.txt$"),  # Only .py and .txt files
        exclude_pattern=re.compile(r"__pycache__"),
        allowed_extensions={".py", ".txt"},
        hide_empty=False,
    )
    tree = DirectoryTree(".", options)
    tree.print_tree()


if __name__ == "__main__":
    main()
