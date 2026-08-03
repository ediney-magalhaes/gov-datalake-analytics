with source as(
    select * from {{ source('siape', 'siape_ativos') }}
),

final as(
    select
    {{ dbt_utils.star(from=source('siape', 'siape_ativos'), except=["data_ingresso_cargofuncao", "data_nomeacao_cargofuncao", "data_ingresso_orgao", "data_inicio_afastamento", "data_termino_afastamento"]) }},
    safe.parse_date('%d/%m/%Y', data_ingresso_cargofuncao) as data_ingresso_cargofuncao,
    safe.parse_date('%d/%m/%Y', data_nomeacao_cargofuncao) as data_nomeacao_cargofuncao,
    safe.parse_date('%d/%m/%Y', data_ingresso_orgao) as data_ingresso_orgao,
    safe.parse_date('%d/%m/%Y', data_inicio_afastamento) as data_inicio_afastamento,
    safe.parse_date('%d/%m/%Y', data_termino_afastamento) as data_termino_afastamento
    from source
)
select * from final