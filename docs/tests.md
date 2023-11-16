---
render_jinja: true
render_macros: true
hide:
  - navigation
---

**These tests are available for `jinjarope.Environment`:**


{% for f in JinjaFile("src/jinjarope/tests.toml").tests %}
{{ f.identifier | md_style(bold=True) | MkHeader }}
{{ (f.identifier ~ f.filter_fn | format_signature) | md_style(code=True) }}
{% for k, v in f.examples.items() %}

{{ f.filter_fn | get_doc(only_summary=True) }}

!!! jinja "Example"
    Jinja call:
    {{ v.template | MkCode(language="jinja") | string | indent }}

    Result: {{ v.template | render_string | md_style(code=True) | string | indent }}


{{ f.filter_fn | MkDocStrings(show_docstring_description=False) | MkAdmonition(collapsible=True, title="DocStrings", typ="quote") }}


{% endfor %}
{% endfor %}
