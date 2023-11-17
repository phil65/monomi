**JinjaRope** uses TOML files to define all jinja filters / tests and add additional information like examples for automatically creating the documentation.

A [jinjarope.JinjaFile][] looks like this:

```toml
 # define a filter with a unique name

[filters.name_of_filter]
fn: "mylibrary.some_function"  # dotted path to the callable.
group: "text"  # used for the documentation
description: # additional description
aliases: ["e"]  # for adding shortcuts / aliases
required_packages: ["my_package"]  # will only add filter / test when given package is installed

# define an example for the docs
[filters.name_of_filter.examples.some_identifier]
title = "Example title"
description = "Some explanation text"
template = """
{ { some jinja example } }
"""

...
```

Tests can be defined in the same way.
```toml
[tests.name_of_test]
... #  same fields as for filters
```

**JinjaRope** contains separate definition files for the **jinja2**-builtin filters / tests
and the **JinjaRope** filters / tests. The **jinja2**-definition files are only used for documenation (that way the documenation contains all filters / tests, so no need to juggle between different docs), the **JinjaRope** definition files will also get loaded by the jinjarope environment.

Additional [JinjaFiles][jinjarope.JinjaFile] can get added to Environments easily via [jinjarope.Environment.load_jinja_file][].
