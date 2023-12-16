from __future__ import annotations

from typing import Literal

import mknodes as mk
from mknodes.manual import dev_section

from jinjarope import inspectfilters, iterfilters, jinjafile, mdfilters


def table_for_items(items) -> mk.MkTable:
    t = mk.MkTable(columns=["Name", "Description"])
    for item in items:
        link = mdfilters.autoref_link(item.identifier, item.identifier)
        doc = inspectfilters.get_doc(item.filter_fn, only_summary=True)
        t.add_row((link, doc))
    return t


class Build:
    @classmethod
    def build(cls, root, theme):
        b = cls()
        # b.on_theme(theme)
        return b.on_root(root)

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
        filters_index = filters_nav.add_page(title, is_index=True, hide="toc")
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
        grouped = iterfilters.groupby(all_items, key="group", natural_sort=True)
        for group, filters in grouped.items():
            p = mk.MkPage(group)
            filters_nav += p
            variables = dict(mode=slug, items=list(filters))
            p += mk.MkTemplate("filters.jinja", variables=variables)
            filters_index += f"## {group}"
            filters_index += table_for_items(filters)


if __name__ == "__main__":
    build = Build()
    nav = mk.MkNav("JinjaRope")
    theme = mk.MaterialTheme()
    build.build(nav, theme)
    print(nav)
