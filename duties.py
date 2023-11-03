from __future__ import annotations

import json

from duty import duty


ENV_PREFIX = "hatch run "

PARAMS = ["--disable-pip-version-check", "--outdated", "--format=json"]
UPDATE_CMD = f"""{ENV_PREFIX}python -m pip list {" ".join(PARAMS)}"""


@duty(capture=False)
def build(ctx):
    """Build a MkNodes page."""
    ctx.run(f"{ENV_PREFIX}mknodes build")


@duty(capture=False)
def serve(ctx, args: str | None = None):
    """Serve a MkNodes page."""
    args = f" {args}" if args else ""
    ctx.run(f"{ENV_PREFIX}mknodes serve{args}")


@duty(capture=False)
def test(ctx, args: str | None = None):
    """Serve a MkNodes page."""
    args = f" {args}" if args else ""
    ctx.run(f"{ENV_PREFIX}pytest{args}")


@duty(capture=False)
def clean(ctx):
    """Clean all files from the Git directory except checked-in files."""
    ctx.run("git clean -dfX")


@duty
def update(ctx):
    """Update all environment packages using pip directly."""
    requirements = ctx.run(UPDATE_CMD)
    requirements = "\n".join(requirements.split("\n")[1:])
    packages = [x["name"] for x in json.loads(requirements)]
    if packages:
        package_str = " ".join(packages)
        print(f"Packages to update: {package_str}")
        ctx.run(f"{ENV_PREFIX}python -m pip install -U {package_str}", capture=False)
    else:
        print("No packages to update!")
    ctx.run(f"{ENV_PREFIX}python -m pip install -e .", capture=False)


@duty(capture=False)
def lint(ctx):
    """Update all environment packages using pip directly."""
    ctx.run(f"{ENV_PREFIX}lint")


@duty(capture=False)
def lint_check(ctx):
    """Update all environment packages using pip directly."""
    ctx.run(f"{ENV_PREFIX}lint-check")
