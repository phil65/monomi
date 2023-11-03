from __future__ import annotations

import contextlib
import logging
import os
import pathlib

from typing import Any

import jinja2

from jinjarope import envglobals, loaders, undefined as undefined_


logger = logging.getLogger(__name__)


class Environment(jinja2.Environment):
    """An enhanced Jinja environment."""

    def __init__(
        self,
        *,
        undefined: undefined_.UndefinedStr | type[jinja2.Undefined] = "strict",
        trim_blocks: bool = True,
        cache_size: int = -1,
        auto_reload: bool = False,
        loader: jinja2.BaseLoader
        | list[jinja2.BaseLoader]
        | dict
        | list[dict]
        | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            undefined: Handling of "Undefined" errors
            trim_blocks: Whitespace handling. Changes jinja default to `True`.
            cache_size: Amount of templates to cache.
                        Changes jinja default to not clean cache.
            auto_reload: Whether to check templates for changes on loading
            loader: Loader to use (Also accepts a JSON representation of loaders)
            kwargs: Keyword arguments passed to parent
        """
        if isinstance(undefined, str):
            undefined = undefined_.UNDEFINED_BEHAVIOR[undefined]
        kwargs = dict(
            undefined=undefined,
            trim_blocks=trim_blocks,
            auto_reload=auto_reload,
            cache_size=cache_size,
            loader=loaders.from_json(loader),
            **kwargs,
        )
        self._extra_files: set[str] = set()
        self._extra_paths: set[str] = set()
        super().__init__(**kwargs)
        self.filters.update(envglobals.ENV_FILTERS)
        self.globals.update(envglobals.ENV_GLOBALS)
        self.filters["render_template"] = self.render_template
        self.filters["render_string"] = self.render_string
        self.filters["render_file"] = self.render_file

    def __contains__(self, template: str | os.PathLike):
        """Check whether given template path exists."""
        return pathlib.Path(template).as_posix() in self.list_templates()

    def __getitem__(self, val: str) -> jinja2.Template:
        """Return a template by path."""
        return self.get_template(val)

    def inherit_from(self, env: jinja2.Environment):
        """Inherit complete configuration from another environment."""
        self.__dict__.update(env.__dict__)
        self.linked_to = env
        self.overlayed = True

    def add_template(self, file: str | os.PathLike):
        """Add a new template during runtime.

        Will create a new DictLoader and inject it into the existing loaders.

        Useful since render_string/render_file does not allow to use a parent template.
        Using this, render_template can be used.

        Arguments:
            file: File to add as a template
        """
        # we keep track of already added extra files to not add things multiple times.
        file = str(file)
        if file in self._extra_files:
            return
        self._extra_files.add(file)
        content = envglobals.load_file_cached(file)
        new_loader = loaders.DictLoader({file: content})
        self._add_loader(new_loader)

    def add_template_path(self, *path: str | os.PathLike):
        """Add a new template path during runtime.

        Will append a new FileSystemLoader by wrapping it and the the current loader into
        either an already-existing or a new Choiceloader.

        Arguments:
            path: Template serch path(s) to add
        """
        for p in path:
            if p in self._extra_paths:
                return
            self._extra_paths.add(str(p))
            new_loader = loaders.FileSystemLoader(p)
            self._add_loader(new_loader)

    def _add_loader(self, new_loader: jinja2.BaseLoader | dict | str | os.PathLike):
        match new_loader:
            case dict():
                new_loader = loaders.DictLoader(new_loader)
            case str() | os.PathLike():
                new_loader = loaders.FileSystemLoader(new_loader)
        match self.loader:
            case jinja2.ChoiceLoader():
                self.loader.loaders = [new_loader, *self.loader.loaders]
            case None:
                self.loader = new_loader
            case _:
                self.loader = loaders.ChoiceLoader(loaders=[new_loader, self.loader])

    def render_string(self, string: str, variables: dict | None = None):
        """Render a template string.

        Arguments:
            string: String to render
            variables: Extra variables for the environment
        """
        cls = self.template_class
        template = cls.from_code(self, self.compile(string), self.globals, None)

        variables = variables or {}
        return template.render(**variables)

    def render_file(
        self,
        file: str | os.PathLike,
        variables: dict | None = None,
    ) -> str:
        """Helper to directly render a template from filesystem.

        Note: The file we pull in gets cached. That should be fine for our case though.

        Arguments:
            file: Template file to load
            variables: Extra variables for the environment
        """
        content = envglobals.load_file_cached(str(file))
        return self.render_string(content, variables)

    def render_template(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
        block_name: str | None = None,
        parent_template: str | None = None,
    ) -> str:
        """Render a loaded template (or a block of a template).

        Arguments:
            template_name: Template name
            variables: Extra variables for this render call
            block_name: Render specific block from the template
            parent_template: The name of the parent template importing this template
        """
        template = self.get_template(template_name, parent=parent_template)
        if not block_name:
            variables = variables or {}
            return template.render(**variables)
        try:
            block_render_func = template.blocks[block_name]
        except KeyError:
            raise BlockNotFoundError(block_name, template_name) from KeyError

        ctx = template.new_context(variables or {})
        return self.concat(block_render_func(ctx))  # type: ignore
        # except Exception:
        #     self.handle_exception()

    @contextlib.contextmanager
    def with_globals(self, **kwargs: Any):
        """Context manager to temporarily set globals for the environment.

        Arguments:
            kwargs: Globals to set
        """
        temp = {}
        for k, v in kwargs.items():
            temp[k] = self.globals.get(k)
            self.globals[k] = v
        yield
        self.globals.update(temp)

    def setup_loader(
        self,
        dir_paths: list[str] | None = None,
        module_paths: list[str] | None = None,
        static: dict[str, str] | None = None,
        fsspec_paths: bool = True,
    ):
        import jinjarope

        self.loader = jinjarope.get_loader(
            dir_paths=dir_paths,
            module_paths=module_paths,
            static=static,
            fsspec_paths=fsspec_paths,
        )


class BlockNotFoundError(Exception):
    def __init__(
        self,
        block_name: str,
        template_name: str,
        message: str | None = None,
    ):
        self.block_name = block_name
        self.template_name = template_name
        super().__init__(
            message
            or f"Block {self.block_name!r} not found in template {self.template_name!r}",
        )


if __name__ == "__main__":
    env = Environment()
    txt = """{% filter indent %}
    test
    {% endfilter %}
    """
    print(env.render_string(txt))
