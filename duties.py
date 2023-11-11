from __future__ import annotations

import json

from duty import duty


ENV_PREFIX = "hatch run "

PARAMS = ["--disable-pip-version-check", "--outdated", "--format=json"]
UPDATE_CMD = f"""{ENV_PREFIX}python -m pip list {" ".join(PARAMS)}"""


@duty(capture=False)
def build(ctx, *args: str):
    """Build a MkNodes page."""
    args_str = " " + " ".join(args) if args else ""
    ctx.run(f"{ENV_PREFIX}mknodes build{args_str}")


@duty(capture=False)
def serve(ctx, *args: str):
    """Serve a MkNodes page."""
    args_str = " " + " ".join(args) if args else ""
    ctx.run(f"{ENV_PREFIX}mknodes serve{args_str}")


@duty(capture=False)
def test(ctx, *args: str):
    """Serve a MkNodes page."""
    args_str = " " + " ".join(args) if args else ""
    ctx.run(f"{ENV_PREFIX}pytest{args_str}")


@duty(capture=False)
def clean(ctx):
    """Clean all files from the Git directory except checked-in files."""
    ctx.run("git clean -dfX")


@duty
def update(ctx, *args: str):
    """Update all environment packages using pip directly."""
    args_str = " " + " ".join(args) if args else ""
    requirements = ctx.run(UPDATE_CMD + args_str)
    requirements = "\n".join(requirements.split("\n")[1:])
    packages = [x["name"] for x in json.loads(requirements)]
    if packages:
        pkgs = " ".join(packages)
        print(f"Packages to update: {pkgs}")
        ctx.run(f"{ENV_PREFIX}python -m pip install -U {pkgs}{args_str}", capture=False)
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


@duty(capture=False)
def version(ctx, *args: str):
    """Bump package version."""
    args_str = " " + " ".join(args) if args else ""
    ctx.run(f"hatch version{args_str}")
