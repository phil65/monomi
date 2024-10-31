from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path


class NodeType(Enum):
    """Types of nodes that can be found in the Python file."""

    MODULE = auto()
    CLASS = auto()
    FUNCTION = auto()
    METHOD = auto()
    STATICMETHOD = auto()
    CLASSMETHOD = auto()
    PROPERTY = auto()
    ASYNC_FUNCTION = auto()
    ASYNC_METHOD = auto()


@dataclass
class Node:
    """Represents a node in the Python file structure."""

    name: str
    type: NodeType
    children: list[Node]
    line_number: int
    decorators: list[str]


@dataclass
class TreeOptions:
    """Configuration options for tree generation."""

    show_types: bool = True
    show_line_numbers: bool = False
    show_decorators: bool = True
    sort_alphabetically: bool = False
    include_private: bool = True
    include_dunder: bool = False
    max_depth: int | None = None
    branch_style: str = "ascii"  # "ascii" or "unicode"

    @property
    def symbols(self) -> dict[str, str]:
        """Return the appropriate tree symbols based on style."""
        if self.branch_style == "unicode":
            return {"pipe": "│   ", "last": "└── ", "branch": "├── ", "empty": "    "}
        return {"pipe": "|   ", "last": "`-- ", "branch": "|-- ", "empty": "    "}


def _get_decorator_names(decorators: list[ast.expr]) -> list[str]:
    """Extract decorator names from AST nodes."""
    names: list[str] = []
    for dec in decorators:
        if isinstance(dec, ast.Name):
            names.append(f"@{dec.id}")
        elif isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name):
                names.append(f"@{dec.func.id}")
            elif isinstance(dec.func, ast.Attribute):
                names.append(f"@{dec.func.attr}")
    return names


def _should_include_node(name: str, options: TreeOptions) -> bool:
    """Determine if a node should be included based on options."""
    if name.startswith("__") and not options.include_dunder:
        return False
    return not (name.startswith("_") and not options.include_private)


def parse_python_file(file_path: Path | str) -> Node:
    """Parse a Python file and return its structure as a tree."""
    if isinstance(file_path, str):
        file_path = Path(file_path)

    with file_path.open("r", encoding="utf-8") as f:
        content = f.read()

    tree = ast.parse(content)
    root = Node(file_path.name, NodeType.MODULE, [], 0, [])

    # Process top-level nodes
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            class_node = Node(
                node.name,
                NodeType.CLASS,
                [],
                node.lineno,
                _get_decorator_names(node.decorator_list),
            )
            root.children.append(class_node)

            # Process class body
            for item in node.body:
                if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                    decorators = _get_decorator_names(item.decorator_list)
                    node_type = NodeType.METHOD

                    # Determine method type based on decorators
                    if "@staticmethod" in decorators:
                        node_type = NodeType.STATICMETHOD
                    elif "@classmethod" in decorators:
                        node_type = NodeType.CLASSMETHOD
                    elif "@property" in decorators:
                        node_type = NodeType.PROPERTY
                    elif isinstance(item, ast.AsyncFunctionDef):
                        node_type = NodeType.ASYNC_METHOD
                    # mypy wants this check
                    assert isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef)
                    method_node = Node(item.name, node_type, [], item.lineno, decorators)
                    class_node.children.append(method_node)

        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            node_type = (
                NodeType.ASYNC_FUNCTION
                if isinstance(node, ast.AsyncFunctionDef)
                else NodeType.FUNCTION
            )
            func_node = Node(
                node.name,
                node_type,
                [],
                node.lineno,
                _get_decorator_names(node.decorator_list),
            )
            root.children.append(func_node)

    return root


def generate_tree(
    node: Node,
    options: TreeOptions,
    prefix: str = "",
    is_last: bool = True,
    depth: int = 0,
) -> str:
    """Generate an ASCII/Unicode tree representation of the structure."""
    if options.max_depth is not None and depth > options.max_depth:
        return ""

    if not _should_include_node(node.name, options):
        return ""

    symbols = options.symbols
    tree = prefix
    tree += symbols["last"] if is_last else symbols["branch"]

    # Build the node label
    label = node.name
    if options.show_types:
        label += f" ({node.type.name})"
    if options.show_line_numbers:
        label += f" [L{node.line_number}]"
    if options.show_decorators and node.decorators:
        label += f" [{', '.join(node.decorators)}]"

    tree += f"{label}\n"

    children = node.children
    if options.sort_alphabetically:
        children = sorted(children, key=lambda x: x.name)

    for i, child in enumerate(children):
        extension = symbols["empty"] if is_last else symbols["pipe"]
        tree += generate_tree(
            child,
            options,
            prefix + extension,
            i == len(children) - 1,
            depth + 1,
        )

    return tree


def create_structure_map(
    file_path: Path | str,
    *,
    show_types: bool = True,
    show_line_numbers: bool = False,
    show_decorators: bool = True,
    sort_alphabetically: bool = False,
    include_private: bool = True,
    include_dunder: bool = False,
    max_depth: int | None = None,
    use_unicode: bool = True,
) -> str:
    """Create a tree representation of a Python file's structure."""
    options = TreeOptions(
        show_types=show_types,
        show_line_numbers=show_line_numbers,
        show_decorators=show_decorators,
        sort_alphabetically=sort_alphabetically,
        include_private=include_private,
        include_dunder=include_dunder,
        max_depth=max_depth,
        branch_style="unicode" if use_unicode else "ascii",
    )

    root = parse_python_file(file_path)
    return generate_tree(root, options)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a tree representation of a Python file's structure"
    )
    parser.add_argument("file", help="Path to the Python file")
    parser.add_argument("--no-types", action="store_true", help="Don't show node types")
    parser.add_argument("--line-numbers", action="store_true", help="Show line numbers")
    parser.add_argument(
        "--no-decorators", action="store_true", help="Don't show decorators"
    )
    parser.add_argument("--sort", action="store_true", help="Sort nodes alphabetically")
    parser.add_argument(
        "--no-private", action="store_true", help="Don't include private members"
    )
    parser.add_argument("--dunder", action="store_true", help="Include dunder methods")
    parser.add_argument("--depth", type=int, help="Maximum depth to display")
    parser.add_argument(
        "--no-unicode", action="store_true", help="Use ASCII characters for the tree"
    )
    args = parser.parse_args()

    tree = create_structure_map(
        args.file,
        show_types=not args.no_types,
        show_line_numbers=args.line_numbers,
        show_decorators=not args.no_decorators,
        sort_alphabetically=args.sort,
        include_private=not args.no_private,
        include_dunder=args.dunder,
        max_depth=args.depth,
        use_unicode=not args.no_unicode,
    )

    print(tree)
    print(
        create_structure_map(
            "src/jinjarope/environment.py",
            show_types=False,
            show_line_numbers=True,
            show_decorators=True,
            sort_alphabetically=True,
            include_private=False,
            include_dunder=False,
            max_depth=2,
            use_unicode=True,
        )
    )
