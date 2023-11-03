__version__ = "0.0.4"


from .environment import Environment
from .loaders import (
    FileSystemLoader,
    FsSpecFileSystemLoader,
    FsSpecProtocolPathLoader,
    ChoiceLoader,
    PackageLoader,
    DictLoader,
)
from .loaderregistry import LoaderRegistry


registry = LoaderRegistry()

get_loader = registry.get_loader

__all__ = [
    "Environment",
    "FsSpecFileSystemLoader",
    "FsSpecProtocolPathLoader",
    "FileSystemLoader",
    "ChoiceLoader",
    "PackageLoader",
    "DictLoader",
    "get_loader",
]
