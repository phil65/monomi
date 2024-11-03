"""YAML handling utilities with enhanced loading and dumping capabilities."""

from __future__ import annotations

import os
from typing import Any, Literal, TypeVar

import fsspec
from mknodes.utils import log
import yaml
import yaml_env_tag
import yaml_include


logger = log.get_logger(__name__)

LoaderStr = Literal["unsafe", "full", "safe"]
LoaderType = type[
    yaml.Loader
    | yaml.CLoader
    | yaml.UnsafeLoader
    | yaml.CUnsafeLoader
    | yaml.FullLoader
    | yaml.CFullLoader
]
DumperType = type[yaml.Dumper | yaml.CDumper]
YamlError = yaml.YAMLError  # Reference for external libs
YAMLPrimitive = str | int | float | bool | None
YAMLValue = YAMLPrimitive | dict[str, Any] | list[Any]
LOADERS: dict[str, LoaderType] = {
    "unsafe": yaml.CUnsafeLoader,
    "full": yaml.CFullLoader,
    "safe": yaml.CSafeLoader,
}
T = TypeVar("T", bound=type)


def map_class_to_builtin_type(dumper_class, class_type, target_type):
    """Maps a Python class to use an existing PyYAML representer for a built-in type.

    The original type is preserved, only the representation format is borrowed.

    Args:
        dumper_class: The YAML Dumper class
        class_type: The custom Python class to map
        target_type: The built-in type whose representer should be used
    """
    method_name = f"represent_{target_type.__name__}"

    if hasattr(dumper_class, method_name):
        representer = getattr(dumper_class, method_name)

        def represent_as_builtin(dumper, data):
            return representer(dumper, data)  # Pass data directly without conversion

        dumper_class.add_representer(class_type, represent_as_builtin)
    else:
        msg = f"No representer found for type {target_type}"
        raise ValueError(msg)


def create_subclass(base_cls: T) -> T:
    """Create a subclass of the given base class to avoid modifying original classes.

    Args:
        base_cls: Base class to inherit from

    Returns:
        New subclass of the base class
    """
    return type("SubClass", (base_cls,), {})  # type: ignore[return-value]


def get_include_constructor(
    fs: str | os.PathLike[str] | fsspec.AbstractFileSystem | None = None,
    **kwargs: Any,
) -> yaml_include.Constructor:
    """Create a YAML include constructor with filesystem support.

    Args:
        fs: Filesystem specification (path or filesystem object)
        kwargs: Additional arguments for the Constructor

    Returns:
        Configured YAML include constructor
    """
    match fs:
        case str() | os.PathLike():
            filesystem, _ = fsspec.url_to_fs(str(fs))
        case None:
            filesystem = fsspec.filesystem("file")
        case fsspec.AbstractFileSystem():
            filesystem = fs
        case _:
            msg = f"Unsupported filesystem type: {type(fs)}"
            raise TypeError(msg)

    return yaml_include.Constructor(fs=filesystem, **kwargs)


def get_safe_loader(base_loader_cls: LoaderType) -> LoaderType:
    """Create a SafeLoader with dummy constructors for common tags.

    Args:
        base_loader_cls: Base loader class to extend

    Returns:
        Enhanced safe loader class
    """
    loader_cls = create_subclass(base_loader_cls)

    # Add dummy constructors for simple tags
    for tag in ("!include", "!relative"):
        loader_cls.add_constructor(tag, lambda loader, node: None)

    # Add dummy constructors for complex tags
    python_tags = (
        "tag:yaml.org,2002:python/name:",
        "tag:yaml.org,2002:python/object/apply:",
    )
    for tag in python_tags:
        loader_cls.add_multi_constructor(tag, lambda loader, suffix, node: None)
    # https://github.com/smart-home-network-security/pyyaml-loaders/
    # loader_cls.add_multi_constructor("!", lambda loader, suffix, node: None)
    return loader_cls


def get_loader(
    base_loader_cls: LoaderType,
    include_base_path: str | os.PathLike[str] | fsspec.AbstractFileSystem | None = None,
    enable_include: bool = True,
    enable_env: bool = True,
) -> LoaderType:
    """Construct an enhanced YAML loader with optional support for !env and !include tags.

    Args:
        base_loader_cls: Base loader class to extend
        include_base_path: Base path for !include tag resolution. If None, use cwd.
        enable_include: Whether to enable !include tag support. Defaults to True
        enable_env: Whether to enable !ENV tag support. Defaults to True

    Returns:
        Enhanced loader class
    """
    loader_cls = create_subclass(base_loader_cls)

    if enable_include:
        constructor = get_include_constructor(fs=include_base_path)
        yaml.add_constructor("!include", constructor, loader_cls)

    if enable_env:
        loader_cls.add_constructor("!ENV", yaml_env_tag.construct_env_tag)

    return loader_cls


def load_yaml(
    text: str,
    mode: LoaderStr = "unsafe",
    include_base_path: str | os.PathLike[str] | fsspec.AbstractFileSystem | None = None,
) -> Any:
    """Load a YAML string with specified safety mode and include path support.

    Args:
        text: YAML content to parse
        mode: Loading mode determining safety level
        include_base_path: Base path for resolving !include tags

    Returns:
        Parsed YAML content
    """
    base_loader_cls: type = LOADERS[mode]
    loader = get_loader(base_loader_cls, include_base_path=include_base_path)
    return yaml.load(text, Loader=loader)


def dump_yaml(
    obj: Any,
    class_mappings: dict[type, type] | None = None,
    **kwargs: Any,
) -> str:
    """Dump a data structure to a YAML string.

    Args:
        obj: Object to serialize
        class_mappings: Dict mapping classes to built-in types for YAML representation
        kwargs: Additional arguments for yaml.dump

    Returns:
        YAML string representation
    """
    dumper_cls = create_subclass(yaml.Dumper)
    if class_mappings:
        for class_type, target_type in class_mappings.items():
            map_class_to_builtin_type(dumper_cls, class_type, target_type)
    return yaml.dump(obj, Dumper=dumper_cls, **kwargs)


if __name__ == "__main__":
    from collections import OrderedDict

    test_data = OrderedDict([("b", 2), ("a", 1)])
    yaml_str = dump_yaml(test_data, class_mappings={OrderedDict: dict})
    print(yaml_str)
    loaded_cfg = load_yaml(yaml_str)
    print(fsspec.url_to_fs("C:/test"))

    print(fsspec.url_to_fs("C:/test"))
