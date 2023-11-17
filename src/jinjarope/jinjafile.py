from __future__ import annotations

from collections.abc import Callable
import dataclasses
import os
import tomllib

import jinjarope

from jinjarope import envglobals, utils


class JinjaFile(dict):
    def __init__(self, path: str | os.PathLike):
        super().__init__()
        text = envglobals.load_file_cached(os.fspath(path))
        data = tomllib.loads(text)
        self.update(data)

    @property
    def filters(self) -> list[JinjaFilter]:
        return [
            JinjaFilter(filter_name, **dct)
            for filter_name, dct in self.get("filters", {}).items()
        ]

    @property
    def tests(self) -> list[JinjaFilter]:
        return [
            JinjaFilter(filter_name, **dct)
            for filter_name, dct in self.get("tests", {}).items()
        ]

    def get_filters_dict(self) -> dict[str, Callable]:
        dct = {}
        for f in self.filters:
            dct[f.identifier] = f.filter_fn
            for alias in f.aliases:
                dct[alias] = f.filter_fn
        return dct

    def get_tests_dict(self) -> dict[str, Callable]:
        dct = {}
        for f in self.tests:
            dct[f.identifier] = f.filter_fn
            for alias in f.aliases:
                dct[alias] = f.filter_fn
        return dct


@dataclasses.dataclass(frozen=True)
class JinjaFilter:
    identifier: str
    fn: str
    group: str
    examples: dict = dataclasses.field(default_factory=dict)
    description: str | None = None
    aliases: list[str] = dataclasses.field(default_factory=list)

    @property
    def filter_fn(self):
        obj = utils.resolve(self.fn)
        if not callable(obj):
            msg = "Filter needs correct, importable Path for callable"
            raise TypeError(msg)
        return obj

    def apply(self, *args, **kwargs):
        self.filter_fn(*args, **kwargs)

    def resolve_example(self, example_name):
        example = self.examples[example_name]
        env = jinjarope.Environment()
        return env.render_string(example["template"])


if __name__ == "__main__":
    file = JinjaFile("src/jinjarope/filters.toml")
    print(file.filters[5].resolve_example("basic"))
    import json

    json.loads("'test'")
