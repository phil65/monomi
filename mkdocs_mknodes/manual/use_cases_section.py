import mknodes as mk

from mknodes.info import mkdocsconfigfile


nav = mk.MkNav("Use cases")


@nav.route.page(is_index=True, hide="toc")
def _(page: mk.MkPage):
    page += mk.MkTemplate("use_cases_index.jinja")


@nav.route.page("Creating a website via config", hide="toc")
def _(page: mk.MkPage):
    """Create the "Creating a sample website" MkPage."""
    file = mkdocsconfigfile.MkDocsConfigFile("configs/mkdocs_mkdocs.yml")
    section = file.get_section("plugins", "mknodes", keep_path=True)
    config = section.serialize("yaml")
    variables = dict(config=config)
    page += mk.MkTemplate("use_case_default_website.jinja", variables=variables)


@nav.route.page("Set MkNode pages via config", hide="toc")
def _(page: mk.MkPage):
    """Create the "Creating a sample website via config" MkPage."""
    file = mkdocsconfigfile.MkDocsConfigFile("configs/mkdocs_mkdocstrings.yml")
    section = file.get_section("plugins", "mknodes", keep_path=True)
    config = section.serialize("yaml")
    variables = dict(config=config)
    page += mk.MkTemplate("use_case_by_config.jinja", variables=variables)


@nav.route.nav("Sub-Websites")
def sub_websites(nav: mk.MkNav):
    page = nav.add_page(is_index=True)
    page += mk.MkTemplate("use_case_subwebsites.jinja")
    # page += mk.MkCode.for_object(sub_websites)
    proj = mk.Project.for_path("https://github.com/mkdocstrings/mkdocstrings.git")
    website_nav = mk.MkDefaultWebsite(section="MkDocStrings", context=proj.context)
    nav += website_nav
