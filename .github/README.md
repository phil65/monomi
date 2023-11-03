``` py title='__main__.create_github_index_md' linenums="86" hl_lines="3"
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
```

# MkNodes (Mkdocs Plugin)

#### Don't write docs. Code them.


[![PyPI License](https://img.shields.io/pypi/l/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Package status](https://img.shields.io/pypi/status/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Daily downloads](https://img.shields.io/pypi/dd/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Weekly downloads](https://img.shields.io/pypi/dw/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Monthly downloads](https://img.shields.io/pypi/dm/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Distribution format](https://img.shields.io/pypi/format/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Wheel availability](https://img.shields.io/pypi/wheel/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Python version](https://img.shields.io/pypi/pyversions/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Implementation](https://img.shields.io/pypi/implementation/mkdocs-mknodes.svg)](https://pypi.org/project/mkdocs-mknodes/)
[![Releases](https://img.shields.io/github/downloads/phil65/mkdocs_mknodes/total.svg)](https://github.com/phil65/monomi/releases)
[![Github Contributors](https://img.shields.io/github/contributors/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/graphs/contributors)
[![Github Discussions](https://img.shields.io/github/discussions/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/discussions)
[![Github Forks](https://img.shields.io/github/forks/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/forks)
[![Github Issues](https://img.shields.io/github/issues/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/issues)
[![Github Issues](https://img.shields.io/github/issues-pr/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/pulls)
[![Github Watchers](https://img.shields.io/github/watchers/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/watchers)
[![Github Stars](https://img.shields.io/github/stars/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/stars)
[![Github Repository size](https://img.shields.io/github/repo-size/phil65/mkdocs_mknodes)](https://github.com/phil65/mkdocs_mknodes)
[![Github last commit](https://img.shields.io/github/last-commit/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/commits)
[![Github release date](https://img.shields.io/github/release-date/phil65/mkdocs_mknodes)](https://github.com/phil65/monomi/releases)
[![Github language count](https://img.shields.io/github/languages/count/phil65/mkdocs_mknodes)](https://github.com/phil65/mkdocs_mknodes)
[![Github commits this week](https://img.shields.io/github/commit-activity/w/phil65/mkdocs_mknodes)](https://github.com/phil65/mkdocs_mknodes)
[![Github commits this month](https://img.shields.io/github/commit-activity/m/phil65/mkdocs_mknodes)](https://github.com/phil65/mkdocs_mknodes)
[![Github commits this year](https://img.shields.io/github/commit-activity/y/phil65/mkdocs_mknodes)](https://github.com/phil65/mkdocs_mknodes)
[![Package status](https://codecov.io/gh/phil65/mkdocs_mknodes/branch/main/graph/badge.svg)](https://codecov.io/gh/phil65/mkdocs_mknodes/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyUp](https://pyup.io/repos/github/phil65/mkdocs_mknodes/shield.svg)](https://pyup.io/repos/github/phil65/mkdocs_mknodes/)

[Read the completely coded documentation!](https://phil65.github.io/mkdocs-mknodes/)

## How to install

### pip

The latest released version is available at the [Python package index](https://pypi.org/project/mknodes).

``` py
pip install mkdocs-mknodes
```

## All the nodes!

``` mermaid
graph LR
  2257944740368["mknode.MkNode"]
  2257944738416["mkheader.MkHeader"]
  2257955065920["mktext.MkText"]
  2257991175136["mkchangelog.MkChangelog"]
  2257991176112["mkcodeofconduct.MkCodeOfConduct"]
  2257952121424["mklicense.MkLicense"]
  2257955088368["mkcontainer.MkContainer"]
  2257955064944["mkblock.MkBlock"]
  2257955089344["mkhtmlblock.MkHtmlBlock"]
  2257955078608["mkadmonitionblock.MkAdmonitionBlock"]
  2257955077632["mkdetailsblock.MkDetailsBlock"]
  2257955160592["mktabs.MkTabBlock"]
  2257955071776["mkadmonition.MkAdmonition"]
  2257955084464["mkblockquote.MkBlockQuote"]
  2257955086416["mkcode.MkCode"]
  2257955158640["mkdiagram.MkDiagram"]
  2257954958560["mkclassdiagram.MkClassDiagram"]
  2257952071648["mktreeview.MkTreeView"]
  2257952109712["mkmoduleoverview.MkModuleOverview"]
  2257952072624["mkprettyprint.MkPrettyPrint"]
  2257952105808["mklog.MkLog"]
  2257955091296["mkfootnotes.MkFootNote"]
  2257955082512["mkfootnotes.MkFootNotes"]
  2257955101056["mkpage.MkPage"]
  2257954988816["mktemplatepage.MkTemplatePage"]
  2257954999552["mkclasspage.MkClassPage"]
  2257954994672["mkmodulepage.MkModulePage"]
  2257955157664["mkgrid.MkGridCard"]
  2257955147904["mkgrid.MkGrid"]
  2257955154736["mklist.MkList"]
  2257955175232["mkbasetable.MkBaseTable"]
  2257955144976["mktable.MkTable"]
  2257954973200["mkclasstable.MkClassTable"]
  2257954940992["mkmoduletable.MkModuleTable"]
  2257952107760["mkdependencytable.MkDependencyTable"]
  2257955159616["mkhtmltable.MkHtmlTable"]
  2257955161568["mktabs.MkTab"]
  2257955162544["mktabcontainer.MkTabContainer"]
  2257955163520["mktabcontainer.MkTabbed"]
  2257952104832["mkreprrawrendered.MkReprRawRendered"]
  2257955164496["mktabcontainer.MkTabbedBlocks"]
  2257955171328["mkcritic.MkCritic"]
  2257955166448["mkannotations.MkAnnotation"]
  2257955168400["mkannotations.MkAnnotations"]
  2257955172304["mkdefinitionlist.MkDefinition"]
  2257952113616["mkconfigsetting.MkConfigSetting"]
  2257955173280["mkdefinitionlist.MkDefinitionList"]
  2257954969296["mkshowcase.MkShowcase"]
  2257954957584["mkspeechbubble.MkSpeechBubble"]
  2257954949776["mktasklist.MkTask"]
  2257954941968["mktasklist.MkTaskList"]
  2257954944896["mkmetadatabadges.MkMetadataBadges"]
  2257954981984["mkshields.MkShields"]
  2257954992720["mkinstallguide.MkInstallGuide"]
  2257991178064["mkcommitconventions.MkCommitConventions"]
  2257991156592["mkpullrequestguidelines.MkPullRequestGuidelines"]
  2257952053104["mkdevenvsetup.MkDevEnvSetup"]
  2257952110688["mkcommentedcode.MkCommentedCode"]
  2257952114592["mkpluginflow.MkPluginFlow"]
  2257952116544["mkargparsehelp.MkArgParseHelp"]
  2257955097152["mknav.MkNav"]
  2257954996624["mkdoc.MkDoc"]
  2257994953952["mkblog.MkBlog"]
  2257955149856["mklink.MkLink"]
  2257955129360["mkkeys.MkKeys"]
  2257955139120["_mkdocstrings.MkDocStrings"]
  2257955131312["mkimage.MkImage"]
  2257955150832["mkbinaryimage.MkBinaryImage"]
  2257954964416["mkbadge.MkBadge"]
  2257955165472["mksnippet.MkSnippet"]
  2257955169376["mkiframe.MkIFrame"]
  2257955170352["mkprogressbar.MkProgressBar"]
  2257954960512["mkcard.MkCard"]
  2257954976128["mkinclude.MkInclude"]
  2257952115568["mkcallable.MkCallable"]
  2257952108736["mkcommandoutput.MkCommandOutput"]
  2257952117520["mkjinjatemplate.MkTemplate"]
  2257944740368 --> 2257944738416
  2257944740368 --> 2257955065920
  2257955065920 --> 2257991175136
  2257955065920 --> 2257991176112
  2257955065920 --> 2257952121424
  2257944740368 --> 2257955088368
  2257955088368 --> 2257955064944
  2257955064944 --> 2257955089344
  2257955064944 --> 2257955078608
  2257955064944 --> 2257955077632
  2257955064944 --> 2257955160592
  2257955088368 --> 2257955071776
  2257955088368 --> 2257955084464
  2257955088368 --> 2257955086416
  2257955086416 --> 2257955158640
  2257955158640 --> 2257954958560
  2257955086416 --> 2257952071648
  2257952071648 --> 2257952109712
  2257955086416 --> 2257952072624
  2257955086416 --> 2257952105808
  2257955088368 --> 2257955091296
  2257955088368 --> 2257955082512
  2257955088368 --> 2257955101056
  2257955101056 --> 2257954988816
  2257954988816 --> 2257954999552
  2257954988816 --> 2257954994672
  2257955088368 --> 2257955157664
  2257955088368 --> 2257955147904
  2257955088368 --> 2257955154736
  2257955088368 --> 2257955175232
  2257955175232 --> 2257955144976
  2257955144976 --> 2257954973200
  2257955144976 --> 2257954940992
  2257955144976 --> 2257952107760
  2257955175232 --> 2257955159616
  2257955088368 --> 2257955161568
  2257955088368 --> 2257955162544
  2257955162544 --> 2257955163520
  2257955163520 --> 2257952104832
  2257955162544 --> 2257955164496
  2257955088368 --> 2257955171328
  2257955088368 --> 2257955166448
  2257955088368 --> 2257955168400
  2257955088368 --> 2257955172304
  2257955172304 --> 2257952113616
  2257955088368 --> 2257955173280
  2257955088368 --> 2257954969296
  2257955088368 --> 2257954957584
  2257955088368 --> 2257954949776
  2257955088368 --> 2257954941968
  2257955088368 --> 2257954944896
  2257955088368 --> 2257954981984
  2257955088368 --> 2257954992720
  2257955088368 --> 2257991178064
  2257955088368 --> 2257991156592
  2257955088368 --> 2257952053104
  2257955088368 --> 2257952110688
  2257955088368 --> 2257952114592
  2257955088368 --> 2257952116544
  2257944740368 --> 2257955097152
  2257955097152 --> 2257954996624
  2257955097152 --> 2257994953952
  2257944740368 --> 2257955149856
  2257944740368 --> 2257955129360
  2257944740368 --> 2257955139120
  2257944740368 --> 2257955131312
  2257955131312 --> 2257955150832
  2257955131312 --> 2257954964416
  2257944740368 --> 2257955165472
  2257944740368 --> 2257955169376
  2257944740368 --> 2257955170352
  2257944740368 --> 2257954960512
  2257944740368 --> 2257954976128
  2257944740368 --> 2257952115568
  2257944740368 --> 2257952108736
  2257944740368 --> 2257952117520
```
