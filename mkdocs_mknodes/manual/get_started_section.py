from __future__ import annotations

import mknodes as mk

from mkdocs_mknodes import paths


nav = mk.MkNav("Getting started")
router = mk.Router()

INTRO = (
    "This section provides an overview about the sequence of operations applied by"
    " **MkNodes** when running the full build process."
)


@router.route_page("MkNodes plugin for MkDocs", hide="toc", is_homepage=True)
def _(page: mk.MkPage):
    page += mk.MkTemplate("index.jinja")


@router.route_page("What is MkNodes?", hide="toc")
def _(page: mk.MkPage):
    page += mk.MkTemplate("why_should_i_use_mknodes.jinja")


@router.route_page("Plugin configuration", hide="toc")
def _(page: mk.MkPage):
    page += mk.MkTemplate("plugin_configuration.jinja")
    eps = page.ctx.metadata.entry_points.get("mkdocs.plugins", [])
    page += mk.MkDocStrings(
        eps[0].load().config_class,
        show_root_toc_entry=False,
        show_if_no_docstring=True,
        heading_level=4,
        show_bases=False,
        show_source=False,
    )


@router.route_page("The build process", hide="toc")
def _(page: mk.MkPage):
    page += INTRO
    page += mk.MkTimeline(paths.RESOURCES / "timeline_data.toml")


@router.route_page("Plugin flow", icon="dev-to", hide="toc")
def _(page: mk.MkPage):
    page += mk.MkPluginFlow()
