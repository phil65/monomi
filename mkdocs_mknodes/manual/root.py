from __future__ import annotations

import mknodes as mk

from mknodes.manual import dev_section

from mkdocs_mknodes.manual import cli_section, get_started_section, use_cases_section


class Build:
    def on_theme(self, theme: mk.MaterialTheme):
        theme.error_page.content = mk.MkAdmonition("Page does not exist!")
        theme.content_area_width = 1300
        theme.tooltip_width = 800

    def on_root(self, nav: mk.MkNav):
        nav.page_template.announcement_bar = mk.MkMetadataBadges("websites")
        get_started_nav = mk.MkNav("Get started", parent=nav)
        get_started_section.router.register_nodes(get_started_nav)
        nav += get_started_nav
        nav += use_cases_section.nav
        nav.add_doc(section_name="API", flatten_nav=True, recursive=True)
        nav += cli_section.nav
        nav += dev_section.nav
        return nav


def build(project: mk.Project[mk.MaterialTheme]) -> mk.MkNav:
    build = Build()
    project.context.env.add_template_path("mkdocs_mknodes/resources")
    build.on_theme(project.theme)
    return build.on_root(project.root) or project.root
