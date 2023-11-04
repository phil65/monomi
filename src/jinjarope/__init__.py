__version__ = "0.0.4"


from .environment import BlockNotFoundError, Environment
from .loaders import (
    FileSystemLoader,
    FsSpecFileSystemLoader,
    FsSpecProtocolPathLoader,
    ChoiceLoader,
    PackageLoader,
    PrefixLoader,
    DictLoader,
)
from .loaderregistry import LoaderRegistry


registry = LoaderRegistry()

get_loader = registry.get_loader

__all__ = [
    "BlockNotFoundError",
    "Environment",
    "FsSpecFileSystemLoader",
    "FsSpecProtocolPathLoader",
    "FileSystemLoader",
    "ChoiceLoader",
    "PackageLoader",
    "PrefixLoader",
    "DictLoader",
    "get_loader",
]
