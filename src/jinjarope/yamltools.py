from __future__ import annotations

import collections
from typing import TYPE_CHECKING, Any, Literal, TypeVar

import fsspec
from mknodes.utils import log
import yaml
import yaml_env_tag
import yaml_include


if TYPE_CHECKING:
    import os


logger = log.get_logger(__name__)

LoaderStr = Literal["unsafe", "full", "safe"]
LoaderType = type[yaml.Loader | yaml.CLoader]
DumperType = type[yaml.Dumper | yaml.CDumper]

# this reference allows other libs to only import jinjarope directly.
YamlError = yaml.YAMLError

T = TypeVar("T", bound=type)


def create_subclass(base_cls: T) -> T:
    """Create a subclass of the given base class.

    Args:
        base_cls: The base class to inherit from

    Returns:
        A new subclass of the base class
    """

    class SubClass(base_cls):  # type: ignore[valid-type]
        """Subclass, used to not modify the pyyaml classes themselves."""

    return SubClass  # type: ignore[return-value]


def get_include_constructor(
    fs: str | os.PathLike[str] | fsspec.AbstractFileSystem | None = None,
    **kwargs: Any,
):
    """Wraps yaml_include.Constructor for allowing a string for filesystem."""
    match fs:
        case str():
            filesystem, _ = fsspec.url_to_fs(fs)
        case None:
            filesystem = fsspec.filesystem("file")
        case fsspec.AbstractFileSystem():
            filesystem = fs
    return yaml_include.Constructor(fs=filesystem, **kwargs)


def patch_to_dump_ordered_dicts_as_dicts(dumper_cls: DumperType):
    """Patches a Dumper to not dump OrderedDicts as python objects, but regular dicts."""

    def map_representer(dumper: yaml.Dumper, data: dict[Any, Any]) -> yaml.MappingNode:
        return dumper.represent_dict(data.items())

    dumper_cls.add_representer(dict, map_representer)
    dumper_cls.add_representer(collections.OrderedDict, map_representer)


def get_safe_loader(base_loader_cls: LoaderType):
    """Return a "SafeLoader" based on given loader.

    The new loader possesses additional dummy constructors for some commonly used tags.

    Arguments:
        base_loader_cls: The loader class to derive the new loader from
    """
    loader_cls = create_subclass(base_loader_cls)
    tags = ["!include", "!relative"]
    for tag in tags:
        loader_cls.add_constructor(tag, lambda loader, node: None)
    tags = ["tag:yaml.org,2002:python/name:", "tag:yaml.org,2002:python/object/apply:"]
    for tag in tags:
        loader_cls.add_multi_constructor(tag, lambda loader, suffix, node: None)
    # https://github.com/smart-home-network-security/pyyaml-loaders/
    # loader_cls.add_multi_constructor("!", lambda loader, suffix, node: None)
    return loader_cls


def get_loader(
    base_loader_cls: LoaderType,
    include_base_path: str | os.PathLike[str] | fsspec.AbstractFileSystem | None = None,
):
    """Construct a loader based on given options.

    By default !env and !include tags are added to the loader.
    See https://github.com/waylan/pyyaml-env-tag
    """
    loader_cls = create_subclass(base_loader_cls)
    constructor = get_include_constructor(fs=include_base_path)
    yaml.add_constructor("!include", constructor, loader_cls)
    loader_cls.add_constructor("!ENV", yaml_env_tag.construct_env_tag)
    loader_cls.add_constructor("!include", yaml_include.Constructor())
    return loader_cls


def load_yaml(
    text: str,
    mode: LoaderStr = "unsafe",
    include_base_path: str | os.PathLike[str] | fsspec.AbstractFileSystem | None = None,
):
    """Load a yaml string.

    Arguments:
        text: the string to load
        mode: the yaml loader mode.
        include_base_path: Base path to use for !include tag
    """
    match mode:
        case "unsafe":
            base_loader_cls: type = yaml.CUnsafeLoader
        case "full":
            base_loader_cls = yaml.CFullLoader
        case _:
            base_loader_cls = yaml.CSafeLoader

    # Derive from global loader to leave the global loader unaltered.
    loader = get_loader(base_loader_cls, include_base_path=include_base_path)
    return yaml.load(text, Loader=loader)


def dump_yaml(obj: Any, ordered_dict_as_dict: bool = False, **kwargs: Any) -> str:
    """Dump a data structure to a yaml string.

    Arguments:
        obj: The object to serialize
        ordered_dict_as_dict: Whether to dump OrderedDict as dict
        kwargs: Keyword arguments passed to yaml.dump
    """
    dumper_cls = create_subclass(yaml.Dumper)
    if ordered_dict_as_dict:
        patch_to_dump_ordered_dicts_as_dicts(dumper_cls)
    return yaml.dump(obj, Dumper=dumper_cls, **kwargs)


if __name__ == "__main__":
    from collections import OrderedDict

    data = OrderedDict([("b", 2), ("a", 1)])
    test = dump_yaml(data)
    print(test)
    cfg = load_yaml(test)
    print(fsspec.url_to_fs("C:/teset"))
