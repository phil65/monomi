__version__ = "0.11.5"


from .environment import BlockNotFoundError, Environment
from .envconfig import EnvConfig
from .loaders import (
    LoaderMixin,
    FileSystemLoader,
    ChoiceLoader,
    ModuleLoader,
    PackageLoader,
    FunctionLoader,
    PrefixLoader,
    DictLoader,
    from_json as get_loader_from_json,
)
from .rewriteloader import RewriteLoader
from .configloaders import NestedDictLoader, TemplateFileLoader
from .fsspecloaders import (
    FsSpecFileSystemLoader,
    FsSpecProtocolPathLoader,
)
from .loaderregistry import LoaderRegistry
from .jinjafile import JinjaFile, JinjaItem

registry = LoaderRegistry()

get_loader = registry.get_loader


def get_loader_cls_by_id(loader_id: str):
    from . import inspectfilters

    loaders = {
        i.ID: i for i in inspectfilters.list_subclasses(LoaderMixin) if "ID" in i.__dict__
    }
    return loaders[loader_id]


__all__ = [
    "BlockNotFoundError",
    "Environment",
    "EnvConfig",
    "FsSpecFileSystemLoader",
    "FsSpecProtocolPathLoader",
    "FileSystemLoader",
    "ChoiceLoader",
    "ModuleLoader",
    "NestedDictLoader",
    "RewriteLoader",
    "TemplateFileLoader",
    "PackageLoader",
    "FunctionLoader",
    "PrefixLoader",
    "DictLoader",
    "get_loader",
    "get_loader_cls_by_id",
    "get_loader_from_json",
    "JinjaFile",
    "JinjaItem",
]
