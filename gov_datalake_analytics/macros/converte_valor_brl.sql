{% macro converte_valor_bruto(coluna) %}
    safe_cast(replace({{coluna}}, ',', '.') as float64)
{% endmacro %}