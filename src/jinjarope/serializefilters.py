from __future__ import annotations

import configparser
import io
import json

from typing import Any, Literal


def serialize(data: Any, fmt: Literal["yaml", "json", "ini", "toml"] | None) -> str:  # type: ignore[return]
    """Serialize given json-like object to given format.

    Arguments:
        data: The data to serialize
        fmt: The serialization format
    """
    match fmt:
        case None | "yaml":
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


def deserialize(data: str, fmt: Literal["yaml", "json", "ini", "toml"] | None) -> Any:  # type: ignore[return]
    """Serialize given json-like object to given format.

    Arguments:
        data: The data to deserialize
        fmt: The serialization format
    """
    match fmt:
        case None | "yaml":
            import yaml

            return yaml.full_load(data)
        case "json":
            return json.loads(data)
        case "ini":
            config = configparser.ConfigParser()
            config.read_string(data)
            return {s: dict(config.items(s)) for s in config.sections()}
        case "toml":
            import tomllib

            return tomllib.loads(data)
        case _:
            raise TypeError(fmt)
