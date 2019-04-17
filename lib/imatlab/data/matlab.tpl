{%- extends 'null.tpl' -%}

{% block header %}
%% Exported from Jupyter Notebook
% Run each section by placing your cursor in it and pressing Ctrl+Enter
{% endblock header %}

{% block in_prompt %}
%% Code Cell[{{ cell.execution_count if cell.execution_count else ' ' }}]:
{% endblock in_prompt %}

{% block input %}
{{ cell.source }}
{% endblock input %}

{% block markdowncell scoped %}
%% Markdown Cell:
{{ cell.source | comment_lines(prefix='% ') }}
{% endblock markdowncell %}
