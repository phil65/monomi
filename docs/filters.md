---
render_jinja: true
render_macros: true
---
{% for f in JinjaFile("src/jinjarope/filters.toml").filters %}
{{ f.identifier | md_style(bold=True) | MkHeader(level=3) }}

{% for k, v in f.examples.items() %}

{{ f.filter_fn | MkDocStrings }}

Jinja call:

{{ v.template | MkCode(language="jinja") }}

Result:

{{ v.template | render_string | MkCode(language="") }}

{% endfor %}
{% endfor %}
