{% for f in items %}
{{ f.identifier | md_style(bold=True) | MkHeader }}
{{ (f.identifier ~ f.filter_fn | format_signature) | md_style(code=True) }}

{{ f.filter_fn | get_doc(only_summary=True) }}

{% if f.aliases %}
**Aliases:** {% for alias in f.aliases %} `{{ alias }}` {% endfor %}
{% endif %}
{% if f.required_packages %}
**Required packages:** {% for required_package in f.required_packages %} `{{ required_package}}` {% endfor %}
{% endif %}

{% for k, v in f.examples.items() %}

!!! jinja "Example"
    Jinja call:
    {{ v.template | MkCode(language="jinja") | string | indent }}

    Result: {{ v.template | render_string | md_style(code=True) | string | indent }}

{% endfor %}

{{ f.filter_fn | MkDocStrings(show_docstring_description=False) | MkAdmonition(collapsible=True, title="DocStrings", typ="quote") }}


{% endfor %}
