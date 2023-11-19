from __future__ import annotations

import itertools

from typing import Literal

import mknodes as mk

from mknodes.manual import dev_section

from jinjarope import jinjafile


class Build:
    def on_root(self, nav: mk.MkNav):
        self.nav = nav
        nav.page_template.announcement_bar = mk.MkMetadataBadges("websites")
        page = nav.add_page(is_index=True, hide="nav,toc")
        page += mk.MkText(page.ctx.metadata.description)
        self.add_section("Filters")
        self.add_section("Tests")
        self.add_section("Functions")
        extending_nav = mk.MkNav("Extensions")
        nav += extending_nav
        page = extending_nav.add_page("Entry points", hide="toc")
        page += mk.MkTemplate("extensions.md")
        page = extending_nav.add_page("JinjaFiles", hide="toc")
        page += mk.MkTemplate("jinjafiles.md")
        nav.add_doc(section_name="API", flatten_nav=True, recursive=True)
        page = nav.add_page("CLI", hide="nav")
        page += mk.MkTemplate("cli.jinja")
        nav += dev_section.nav
        return nav

    def add_section(self, title: Literal["Filters", "Tests", "Functions"]):
        filters_nav = self.nav.add_nav(title)
        filters_index = filters_nav.add_page(title, is_index=True)
        slug = title.lower()
        rope_file = jinjafile.JinjaFile(f"src/jinjarope/resources/{slug}.toml")
        jinja_file = jinjafile.JinjaFile(f"src/jinjarope/resources/jinja_{slug}.toml")
        match slug:
            case "filters":
                jinja_items = jinja_file.filters
                rope_items = rope_file.filters
            case "tests":
                jinja_items = jinja_file.tests
                rope_items = rope_file.tests
            case "functions":
                jinja_items = jinja_file.functions
                rope_items = rope_file.functions
        all_items = rope_items + jinja_items
        if slug == "functions":
            slug = "filters"
        filters_index += mk.MkTemplate(f"{slug}.md", variables=dict(items=all_items))
        for group, filters in itertools.groupby(all_items, key=lambda x: x.group):
            p = mk.MkPage(group)
            filters_nav += p
            p += mk.MkTemplate(f"{slug}.md", variables=dict(items=list(filters)))


def build(project) -> mk.MkNav:
    build = Build()
    return build.on_root(project.root) or project.root
