import mknodes as mk


DOC_URL = "https://phil65.github.io/mkdocs-mknodes/"


def create_github_index_md() -> mk.MkPage:
    page = mk.MkPage("Github index")
    page += mk.MkCode.for_object(create_github_index_md)
    page += mk.MkHeader("MkNodes", level=1)
    page += mk.MkHeader("Don't write docs. Code them.", level=4)
    page += mk.MkShields()
    page += mk.MkLink(DOC_URL, "Read the completely coded documentation!")
    page += mk.MkInstallGuide(header="How to install")
    page += mk.MkHeader("All the nodes!")
    page += mk.MkClassDiagram(mk.MkNode, mode="subclasses", direction="LR")
    return page
