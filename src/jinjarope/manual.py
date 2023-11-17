from __future__ import annotations

import itertools

import mknodes as mk

from mknodes.manual import dev_section

from jinjarope import jinjafile


class Build:
    def on_root(self, nav: mk.MkNav):
        self.nav = nav
        nav.page_template.announcement_bar = mk.MkMetadataBadges("websites")
        page = nav.add_page(is_index=True, hide="toc")
        page += mk.MkText(page.ctx.metadata.description)
        self.add_section("Filters")
        self.add_section("Tests")
        page = nav.add_page("Extensions", hide="toc,nav")
        page += mk.MkTemplate("extensions.md")
        nav.add_doc(section_name="API", flatten_nav=True, recursive=True)
        nav += dev_section.nav
        return nav

    def add_section(self, title: str):
        filters_nav = self.nav.add_nav(title)
        filters_index = filters_nav.add_page(title, is_index=True)
        slug = title.lower()
        rope_file = jinjafile.JinjaFile(f"src/jinjarope/{slug}.toml")
        jinja_file = jinjafile.JinjaFile(f"src/jinjarope/jinja_{slug}.toml")
        if slug == "filters":
            jinja_filters = jinja_file.filters
            rope_filters = rope_file.filters
        else:
            jinja_filters = jinja_file.tests
            rope_filters = rope_file.tests
        all_filters = rope_filters + jinja_filters
        filters_index += mk.MkTemplate(f"{slug}.md", variables=dict(items=all_filters))
        # print(all_filters)
        for group, filters in itertools.groupby(all_filters, key=lambda x: x.group):
            # print(group)
            p = mk.MkPage(group)
            filters_nav += p
            p += mk.MkTemplate(f"{slug}.md", variables=dict(items=list(filters)))


def build(project: mk.Project[mk.MaterialTheme]) -> mk.MkNav:
    build = Build()
    return build.on_root(project.root) or project.root
