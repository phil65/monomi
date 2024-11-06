"""Jinja2 template tag extensions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar
import warnings

from jinja2 import nodes
from jinja2.ext import Extension
from jinja2.lexer import describe_token


if TYPE_CHECKING:
    from collections.abc import Sequence

    from jinja2.environment import Environment
    from jinja2.parser import Parser
    from jinja2.runtime import Context


__all__ = ["StandaloneTag", "ContainerTag", "InclusionTag"]
__version__ = "0.6.1"


class BaseTemplateTag(Extension):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        self.context: Context | None = None
        self.template: str | None = None
        self.lineno: int | None = None
        self.tag_name: str | None = None

    def parse(self, parser: Parser) -> nodes.Node:
        lineno = parser.stream.current.lineno
        tag_name = parser.stream.current.value
        additional_params = [
            nodes.Keyword("_context", nodes.ContextReference()),
            nodes.Keyword("_template", nodes.Const(parser.name)),
            nodes.Keyword("_lineno", nodes.Const(lineno)),
            nodes.Keyword("_tag_name", nodes.Const(tag_name)),
        ]

        self.init_parser(parser)
        args, kwargs, options = self.parse_args(parser)
        kwargs.extend(additional_params)
        options["tag_name"] = tag_name

        if hasattr(self, "output") and callable(self.output):
            warnings.warn(
                'The "output" method of the "BaseTemplateTag" class is deprecated '
                'and will be removed in a future version. Please use the "create_node" '
                "method instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            call_node = self.call_method("render_wrapper", args, kwargs, lineno=lineno)
            return self.output(parser, call_node, lineno=lineno, **options)  # type: ignore

        return self.create_node(parser, args, kwargs, lineno=lineno, **options)

    def init_parser(self, parser: Parser) -> None:
        parser.stream.skip(1)  # skip tag name

    def parse_args(
        self,
        parser: Parser,
    ) -> tuple[list[nodes.Expr], list[nodes.Keyword], dict[str, Any]]:
        args: list[nodes.Expr] = []
        kwargs: list[nodes.Keyword] = []
        options: dict[str, str | None] = {"target": None}
        require_comma = False
        arguments_finished = False

        while parser.stream.current.type != "block_end":
            if parser.stream.current.test("name:as"):
                parser.stream.skip(1)
                options["target"] = parser.stream.expect("name").value
                arguments_finished = True

            if arguments_finished:
                if not parser.stream.current.test("block_end"):
                    parser.fail(
                        "expected token 'block_end', "
                        f"got {describe_token(parser.stream.current)!r}",
                        parser.stream.current.lineno,
                    )
                break

            if require_comma:
                parser.stream.expect("comma")

                # support for trailing comma
                if parser.stream.current.type == "block_end":
                    break

            if (
                parser.stream.current.type == "name"
                and parser.stream.look().type == "assign"
            ):
                key = parser.stream.current.value
                parser.stream.skip(2)
                value = parser.parse_expression()
                kwargs.append(nodes.Keyword(key, value, lineno=value.lineno))
            else:
                if kwargs:
                    parser.fail("Invalid argument syntax", parser.stream.current.lineno)
                args.append(parser.parse_expression())

            require_comma = True

        return args, kwargs, options

    def create_node(
        self,
        parser: Parser,
        args: list[nodes.Expr],
        kwargs: list[nodes.Keyword],
        *,
        lineno: int,
        **options: Any,
    ) -> nodes.Node:
        raise NotImplementedError


class StandaloneTag(BaseTemplateTag):
    safe_output: ClassVar[bool] = False

    def create_node(
        self,
        parser: Parser,
        args: list[nodes.Expr],
        kwargs: list[nodes.Keyword],
        *,
        lineno: int,
        **options: Any,
    ) -> nodes.Node:
        call_node: nodes.Call | nodes.MarkSafeIfAutoescape = self.call_method(
            "render_wrapper",
            args,
            kwargs,
            lineno=lineno,
        )
        if self.safe_output:
            call_node = nodes.MarkSafeIfAutoescape(call_node, lineno=lineno)

        target = options.get("target")
        if target:
            target_node = nodes.Name(target, "store", lineno=lineno)
            return nodes.Assign(target_node, call_node, lineno=lineno)

        return nodes.Output([call_node], lineno=lineno)

    def render_wrapper(self, *args: Any, **kwargs: Any) -> Any:
        self.context = kwargs.pop("_context")
        self.template = kwargs.pop("_template")
        self.lineno = kwargs.pop("_lineno")
        self.tag_name = kwargs.pop("_tag_name")
        return self.render(*args, **kwargs)

    def render(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class ContainerTag(BaseTemplateTag):
    def create_node(
        self,
        parser: Parser,
        args: list[nodes.Expr],
        kwargs: list[nodes.Keyword],
        *,
        lineno: int,
        **options: Any,
    ) -> nodes.Node:
        call_node = self.call_method("render_wrapper", args, kwargs, lineno=lineno)
        body = parser.parse_statements(
            (f"name:end{options['tag_name']}",),
            drop_needle=True,
        )
        call_block = nodes.CallBlock(call_node, [], [], body).set_lineno(lineno)

        target = options.get("target")
        if target:
            target_node = nodes.Name(target, "store", lineno=lineno)
            return nodes.AssignBlock(target_node, None, [call_block], lineno=lineno)
        return call_block

    def render_wrapper(self, *args: Any, **kwargs: Any) -> Any:
        self.context = kwargs.pop("_context")
        self.template = kwargs.pop("_template")
        self.lineno = kwargs.pop("_lineno")
        self.tag_name = kwargs.pop("_tag_name")
        return self.render(*args, **kwargs)

    def render(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class InclusionTag(StandaloneTag):
    template_name: str | None = None
    safe_output: ClassVar[bool] = True

    def render(self, *args: Any, **kwargs: Any) -> str:
        template_names = self.get_template_names(*args, **kwargs)
        if isinstance(template_names, str):
            template = self.environment.get_template(template_names)
        else:
            template = self.environment.select_template(template_names)

        context = template.new_context(
            {
                **self.context.get_all(),  # type: ignore
                **self.get_context(*args, **kwargs),
            },
            shared=True,
        )
        return template.render(context)

    def get_context(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {}

    def get_template_names(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> str | Sequence[str]:
        if self.template_name is None:
            msg = (
                "InclusionTag requires either a definition of 'template_name' "
                "or an implementation of 'get_template_names()'"
            )
            raise RuntimeError(msg)
        return self.template_name


if __name__ == "__main__":
    import hmac

    import jinja2

    class HMACExtension(ContainerTag):
        tags = {"hmac"}  # noqa: RUF012

        def render(self, secret, digest="sha256", caller=None):
            content = str(caller()).encode()

            if isinstance(secret, str):
                secret = secret.encode()

            signing = hmac.new(secret, content, digestmod=digest)
            return signing.hexdigest()

    env = jinja2.Environment(extensions=[HMACExtension])
    template = env.from_string(
        "{% hmac 'SECRET', digest='sha1' %}Hello world!{% endhmac %}"
    )
    print(template.render())
