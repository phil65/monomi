---
render_jinja: true
render_macros: true
hide:
  - navigation
---

**These filters are available for `jinjarope.Environment`:**


{% for f in JinjaFile("src/jinjarope/filters.toml").filters + JinjaFile("src/jinjarope/jinja_filters.toml").filters %}
{{ f.identifier | md_style(bold=True) | MkHeader }}
{{ (f.identifier ~ f.filter_fn | format_signature) | md_style(code=True) }}
{% for k, v in f.examples.items() %}

{{ f.filter_fn | get_doc(only_summary=True) }}

!!! jinja "Example"
    Jinja call:
    {{ v.template | MkCode(language="jinja") | string | indent }}

    Result:

    {{ v.template | render_string | MkCode(language="") | string | indent }}


{{ f.filter_fn | MkDocStrings(show_docstring_description=False) | MkAdmonition(collapsible=True, title="DocStrings") }}


{% endfor %}
{% endfor %}
