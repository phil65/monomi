from __future__ import annotations

import ast
import contextlib
import io
import logging
import os
import pathlib
import time

from types import CodeType
from typing import Any, Literal, overload
import weakref

import jinja2

from jinja2.exceptions import TemplateSyntaxError
import jinja2.nodes

import jinjarope

from jinjarope import (
    envconfig,
    envglobals,
    jinjafile,
    loaders,
    undefined as undefined_,
    utils,
)


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
        loader: (
            jinja2.BaseLoader | list[jinja2.BaseLoader] | dict | list[dict] | None
        ) = None,
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
        self.cache_code = True
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

        # Update namespaces
        folder = pathlib.Path(__file__).parent / "resources"
        self.load_jinja_file(folder / "filters.toml")
        self.load_jinja_file(folder / "tests.toml")
        self.load_jinja_file(folder / "functions.toml")
        self.globals.update(envglobals.ENV_GLOBALS)
        for fn in utils._entry_points("jinjarope.environment").values():
            fn(self)
        self.filters["render_template"] = self.render_template
        self.filters["render_string"] = self.render_string
        self.filters["render_file"] = self.render_file
        self.filters["evaluate"] = self.evaluate
        self.globals["filters"] = self.filters
        self.globals["tests"] = self.tests
        self.tests["template"] = lambda template_name: template_name in self
        self.template_cache: weakref.WeakValueDictionary[
            str | jinja2.nodes.Template,
            CodeType | str | None,
        ] = weakref.WeakValueDictionary()
        self.add_extension("jinja2.ext.loopcontrols")
        self.add_extension("jinja2.ext.do")

    def __contains__(self, template: str | os.PathLike) -> bool:
        """Check whether given template path exists.

        Arguments:
            template: The template path to check
        """
        return pathlib.Path(template).as_posix() in self.list_templates()

    def __getitem__(self, val: str) -> jinja2.Template:
        """Return a template by path.

        val: The template path
        """
        return self.get_template(val)

    def set_undefined(self, value: undefined_.UndefinedStr | type[jinja2.Undefined]):
        """Set the undefined behaviour for the environment.

        Arguments:
            value: The new undefined behaviour
        """
        new = undefined_.UNDEFINED_BEHAVIOR[value] if isinstance(value, str) else value
        self.undefined = new

    def load_jinja_file(
        self,
        path: str | os.PathLike,
        scope_prefix: str = "",
        load_filters: bool = True,
        load_tests: bool = True,
        load_functions: bool = True,
        load_config: bool = True,
        load_loader: bool = True,
    ):
        """Load the content of a JinjaFile and add it to the environment.

        Arguments:
            path: The path to the JinjaFile
            scope_prefix: Optional prefix to add to all tests / filters / functions
            load_filters: Whether to load filters from the JinjaFile
            load_tests: Whether to load tests from the JinjaFile
            load_functions: Whether to load functions from the JinjaFile
            load_config: Whether to load the environment config from the JinjaFile
            load_loader: Whether to load the Loader from the JinjaFile
        """
        file = jinjafile.JinjaFile(path)
        if load_filters:
            dct = {f"{scope_prefix}{k}": v for k, v in file.filters_dict.items()}
            self.filters.update(dct)
        if load_tests:
            dct = {f"{scope_prefix}{k}": v for k, v in file.tests_dict.items()}
            self.tests.update(dct)
        if load_functions:
            dct = {f"{scope_prefix}{k}": v for k, v in file.functions_dict.items()}
            self.globals.update(dct)
        if load_config:
            self.__dict__.update(file.envconfig.as_dict())
        if load_loader and (loader := file.loader):
            self._add_loader(loader)

    @overload
    def compile(  # type: ignore[misc]  # noqa: A003
        self,
        source: str | jinja2.nodes.Template,
        name: str | None = None,
        filename: str | None = None,
        raw: Literal[False] = False,
        defer_init: bool = False,
    ) -> CodeType: ...

    @overload
    def compile(  # noqa: A003
        self,
        source: str | jinja2.nodes.Template,
        name: str | None = None,
        filename: str | None = None,
        raw: Literal[True] = ...,
        defer_init: bool = False,
    ) -> str: ...

    def compile(  # noqa: A003
        self,
        source: str | jinja2.nodes.Template,
        name: str | None = None,
        filename: str | None = None,
        raw: bool = False,
        defer_init: bool = False,
    ) -> CodeType | str:
        """Compile the template."""
        if (
            not self.cache_code
            or name is not None
            or filename is not None
            or raw is not False
            or defer_init is not False
        ):
            # If there are any non-default keywords args, we do
            # not cache.
            return super().compile(  # type: ignore[no-any-return,call-overload]
                source,
                name,
                filename,
                raw,
                defer_init,
            )

        if (cached := self.template_cache.get(source)) is None:
            cached = self.template_cache[source] = super().compile(source)

        return cached

    def inherit_from(self, env: jinja2.Environment):
        """Inherit complete configuration from another environment.

        Arguments:
            env: The environment to inherit settings from
        """
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

    def render_condition(
        self,
        string: str,
        variables: dict | None = None,
        **kwargs: Any,
    ) -> bool:
        """Render a template condition.

        Returns True for true-ish return values from a render_string call.

        Arguments:
            string: String to evaluate for True-ishness
            variables: Extra variables for the rendering
            kwargs: Further extra variables for rendering
        """
        result = self.render_string(string=string, variables=variables, **kwargs)
        return result not in ["None", "False", ""]

    def render_string(
        self,
        string: str,
        variables: dict | None = None,
        **kwargs: Any,
    ) -> str:
        """Render a template string.

        Arguments:
            string: String to render
            variables: Extra variables for the rendering
            kwargs: Further extra variables for rendering
        """
        variables = (variables or {}) | kwargs
        cls = self.template_class
        try:
            template = cls.from_code(self, self.compile(string), self.globals, None)
        except TemplateSyntaxError as e:
            msg = f"Error when evaluating \n{string}\n (extra globals: {variables})"
            raise SyntaxError(msg) from e
        return template.render(**variables)

    def render_file(
        self,
        file: str | os.PathLike,
        variables: dict | None = None,
        **kwargs: Any,
    ) -> str:
        """Helper to directly render a template from filesystem.

        Note: The file we pull in gets cached. That should be fine for our case though.

        Arguments:
            file: Template file to load
            variables: Extra variables for the rendering
            kwargs: Further extra variables for rendering
        """
        content = envglobals.load_file_cached(str(file))
        return self.render_string(content, variables, **kwargs)

    def render_template(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
        block_name: str | None = None,
        parent_template: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Render a loaded template (or a block of a template).

        Arguments:
            template_name: Template name
            variables: Extra variables for rendering
            block_name: Render specific block from the template
            parent_template: The name of the parent template importing this template
            kwargs: Further extra variables for rendering
        """
        variables = (variables or {}) | kwargs
        template = self.get_template(template_name, parent=parent_template)
        if not block_name:
            return template.render(**variables)
        try:
            block_render_func = template.blocks[block_name]
        except KeyError:
            raise BlockNotFoundError(block_name, template_name) from KeyError

        ctx = template.new_context(variables)
        return self.concat(block_render_func(ctx))  # type: ignore
        # except Exception:
        #     self.handle_exception()

    @contextlib.contextmanager
    def with_globals(self, **kwargs: Any):
        """Context manager to temporarily set globals for the environment.

        Arguments:
            kwargs: Globals to set
        """
        temp = self.globals.copy()
        self.globals.update(kwargs)
        yield
        self.globals = temp

    def setup_loader(
        self,
        dir_paths: list[str] | None = None,
        module_paths: list[str] | None = None,
        static: dict[str, str] | None = None,
        fsspec_paths: bool = True,
    ):
        self.loader = jinjarope.get_loader(
            dir_paths=dir_paths,
            module_paths=module_paths,
            static=static,
            fsspec_paths=fsspec_paths,
        )

    def evaluate(
        self,
        code: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Evaluate python code and return the caught stdout + return value of last line.

        Arguments:
            code: The code to execute
            context: Globals for the execution evironment
        """
        now = time.time()
        logger.debug("Evaluating code:\n%s", code)
        tree = ast.parse(code)
        eval_expr = ast.Expression(tree.body[-1].value)  # type: ignore
        # exec_expr = ast.Module(tree.body[:-1])  # type: ignore
        exec_expr = ast.parse("")
        exec_expr.body = tree.body[:-1]
        compiled = compile(exec_expr, "file", "exec")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exec(compiled, self.globals)
            val = eval(compile(eval_expr, "file", "eval"), self.globals)
        logger.debug("Code evaluation took %s seconds.", time.time() - now)
        # result = mk.MkContainer([buffer.getvalue(), val])
        return val or ""

    def get_config(self) -> envconfig.EnvConfig:
        """All environment settings as a dict (not included: undefined and loaders)."""
        return envconfig.EnvConfig(
            block_start_string=self.block_start_string,
            block_end_string=self.block_end_string,
            variable_start_string=self.variable_start_string,
            variable_end_string=self.variable_end_string,
            comment_start_string=self.comment_start_string,
            comment_end_string=self.comment_end_string,
            line_statement_prefix=self.line_statement_prefix,
            line_comment_prefix=self.line_comment_prefix,
            trim_blocks=self.trim_blocks,
            lstrip_blocks=self.lstrip_blocks,
            newline_sequence=self.newline_sequence,
            keep_trailing_newline=self.keep_trailing_newline,
        )


class BlockNotFoundError(Exception):
    """Exception for not-found template blocks."""

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
