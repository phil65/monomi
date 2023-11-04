__version__ = "0.0.6"


from .environment import BlockNotFoundError, Environment
from .loaders import (
    FileSystemLoader,
    FsSpecFileSystemLoader,
    FsSpecProtocolPathLoader,
    ChoiceLoader,
    PackageLoader,
    FunctionLoader,
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
    "FunctionLoader",
    "PrefixLoader",
    "DictLoader",
    "get_loader",
]
