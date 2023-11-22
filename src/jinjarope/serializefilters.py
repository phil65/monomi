from __future__ import annotations

import configparser
import io
import json

from typing import Any, Literal


def serialize(data: Any, fmt: Literal["yaml", "json", "ini", "toml"]) -> str:  # type: ignore[return]
    """Serialize given json-like object to given format.

    Arguments:
        data: The data to serialize
        fmt: The serialization format
    """
    match fmt:
        case "yaml":
            import yaml

            return yaml.dump(data)
        case "json":
            return json.dumps(data, indent=4)
        case "ini":
            config = configparser.ConfigParser()
            config.read_dict(data)
            file = io.StringIO()
            with file as fp:
                config.write(fp)
                return file.getvalue()
        case "toml" if isinstance(data, dict):
            import tomli_w

            return tomli_w.dumps(data)
        case _:
            raise TypeError(fmt)


def load_ini(data: str) -> dict[str, dict[str, str]]:
    config = configparser.ConfigParser()
    config.read_string(data)
    return {s: dict(config.items(s)) for s in config.sections()}


def deserialize(data: str, fmt: Literal["yaml", "json", "ini", "toml"]) -> Any:  # type: ignore[return]
    """Serialize given json-like object to given format.

    Arguments:
        data: The data to deserialize
        fmt: The serialization format
    """
    match fmt:
        case "yaml":
            import yaml

            return yaml.full_load(data)
        case "json":
            return json.loads(data)
        case "ini":
            return load_ini(data)
        case "toml":
            import tomllib

            return tomllib.loads(data)
        case _:
            raise TypeError(fmt)


def dig(
    data: dict,
    *sections: str,
    keep_path: bool = False,
    dig_yaml_lists: bool = True,
):
    """Try to get data with given section path from a dict-list structure.

    If a list is encountered and dig_yaml_lists is true, treat it like a list of
    {"identifier", {subdict}} items, as used in MkDocs config for
    plugins & extensions.
    If Key path does not exist, return None.

    Arguments:
        data: The data to dig into
        sections: Sections to dig into
        keep_path: Return result with original nesting
        dig_yaml_lists: Also dig into single-key->value pairs, as often found in yaml.
    """
    for i in sections:
        if isinstance(data, dict):
            if child := data.get(i):
                data = child
            else:
                return None
        elif dig_yaml_lists and isinstance(data, list):
            # this part is for yaml-style listitems
            for idx in data:
                if i in idx and isinstance(idx, dict):
                    data = idx[i]
                    break
                if isinstance(idx, str) and idx == i:
                    data = idx
                    break
            else:
                return None
    if not keep_path:
        return data
    result: dict[str, dict] = {}
    new = result
    for sect in sections:
        result[sect] = data if sect == sections[-1] else {}
        result = result[sect]
    return new
