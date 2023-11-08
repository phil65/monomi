__version__ = "0.1.4"


from .environment import BlockNotFoundError, Environment
from .loaders import (
    FileSystemLoader,
    FsSpecFileSystemLoader,
    FsSpecProtocolPathLoader,
    ChoiceLoader,
    ModuleLoader,
    NestedDictLoader,
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
    "ModuleLoader",
    "NestedDictLoader",
    "PackageLoader",
    "FunctionLoader",
    "PrefixLoader",
    "DictLoader",
    "get_loader",
]
