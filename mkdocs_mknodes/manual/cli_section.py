import mknodes as mk


# this is the nav we will populate via decorators.
nav = mk.MkNav("CLI")

CLI_PATH = "mkdocs_mknodes.cli:cli"


@nav.route.page(is_index=True, hide="toc")
def _(page: mk.MkPage):
    page += mk.MkBinaryImage.for_file("docs/assets/cli.gif")
    page += mk.MkTemplate("cli_index.jinja")


@nav.route.page("build", icon="wrench")
def _(page: mk.MkPage):
    page += mk.MkClickDoc(CLI_PATH, prog_name="build")


@nav.route.page("serve", icon="web")
def _(page: mk.MkPage):
    page += mk.MkClickDoc(CLI_PATH, prog_name="serve")


@nav.route.page("create-config", icon="folder-wrench")
def _(page: mk.MkPage):
    page += mk.MkClickDoc(CLI_PATH, prog_name="create-config")
