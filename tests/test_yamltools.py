import os
import pathlib

import pytest
import yaml

from jinjarope import yamltools


def test_basic_load():
    assert yamltools.load_yaml("foo: bar") == {"foo": "bar"}
    assert yamltools.load_yaml("[1, 2, 3]") == [1, 2, 3]
    assert yamltools.load_yaml("42") == 42  # noqa: PLR2004


def test_load_modes():
    yaml_str = "!!python/name:os.system"
    with pytest.raises(yaml.constructor.ConstructorError):
        yamltools.load_yaml(yaml_str, mode="safe")
    assert yamltools.load_yaml(yaml_str, mode="unsafe") is os.system


def test_env_tag():
    os.environ["TEST_VAR"] = "42"
    assert yamltools.load_yaml("!ENV TEST_VAR") == 42  # noqa: PLR2004
    assert yamltools.load_yaml("!ENV [NONEXISTENT]") is None
    assert yamltools.load_yaml("!ENV [NONEXISTENT, 'default']") == "default"


@pytest.fixture
def temp_yaml_file(tmp_path: pathlib.Path) -> pathlib.Path:
    content = "test: value"
    file_path = tmp_path / "test.yaml"
    file_path.write_text(content)
    return file_path


def test_include_constructor(temp_yaml_file: pathlib.Path):
    yaml_str = f"!include {temp_yaml_file!s}"
    result = yamltools.load_yaml(yaml_str)
    assert result == {"test": "value"}


def test_dump_yaml():
    data = {"a": 1, "b": [2, 3, 4], "c": {"d": 5}}
    dumped = yamltools.dump_yaml(data)
    assert yamltools.load_yaml(dumped) == data


def test_invalid_yaml():
    with pytest.raises(yaml.YAMLError):
        yamltools.load_yaml("{invalid: yaml: content")


def test_empty_yaml():
    assert yamltools.load_yaml("") is None
    assert yamltools.load_yaml("   ") is None


def test_safe_loader():
    loader = yamltools.get_safe_loader(yaml.SafeLoader)
    assert loader.yaml_constructors["!relative"] is not None


def test_object_roundtrip():
    from collections import OrderedDict

    data = OrderedDict([("b", 2), ("a", 1)])
    dumped = yamltools.dump_yaml(data)
    assert data == yamltools.load_yaml(dumped)


if __name__ == "__main__":
    pytest.main([__file__])
