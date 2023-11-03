import mknodes as mk


def build(project: mk.Project[mk.MaterialTheme]):
    index_page = project.root.add_page(is_index=True, hide="toc")
    index_page += "## Sub-Pages"
    websites = dict(
        ruff="https://github.com/astral-sh/ruff.git",
        MkDocStrings="https://github.com/mkdocstrings/mkdocstrings.git",
        MkDocs="https://github.com/mkdocs/mkdocs.git",
    )
    for k, v in websites.items():
        subproject = mk.Project.for_path(v)
        website_nav = mk.MkDefaultWebsite(section=k, context=subproject.context)
        project.root += website_nav
        index_page += mk.MkLink(target=website_nav, title=k, icon="link")
