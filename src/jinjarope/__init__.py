__version__ = "0.1.8"


from .environment import BlockNotFoundError, Environment
from .loaders import (
    LoaderMixin,
    FileSystemLoader,
    FsSpecFileSystemLoader,
    FsSpecProtocolPathLoader,
    ChoiceLoader,
    ModuleLoader,
    NestedDictLoader,
    TemplateFileLoader,
    PackageLoader,
    FunctionLoader,
    PrefixLoader,
    DictLoader,
)
from .loaderregistry import LoaderRegistry
from . import utils

registry = LoaderRegistry()

get_loader = registry.get_loader


def get_loader_cls_by_id(loader_id: str):
    loaders = {i.ID: i for i in utils.iter_subclasses(LoaderMixin) if "ID" in i.__dict__}
    return loaders[loader_id]


__all__ = [
    "BlockNotFoundError",
    "Environment",
    "FsSpecFileSystemLoader",
    "FsSpecProtocolPathLoader",
    "FileSystemLoader",
    "ChoiceLoader",
    "ModuleLoader",
    "NestedDictLoader",
    "TemplateFileLoader",
    "PackageLoader",
    "FunctionLoader",
    "PrefixLoader",
    "DictLoader",
    "get_loader",
    "get_loader_cls_by_id",
]
