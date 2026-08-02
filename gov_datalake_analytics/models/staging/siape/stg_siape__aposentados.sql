with source as(
    select *
    from {{ source('siape', 'siape_aposentados') }}
), 

final as(
    select
        {{ dbt_utils.star(from=source('siape', 'siape_aposentados'), except=['data_ingresso_cargofuncao', 'data_nomeacao_cargofuncao',
                                                                             'data_ingresso_orgao', 'data_aposentadoria', 'nome']) }},
        safe.parse_date('%d/%m/%Y', data_ingresso_cargofuncao) as data_ingresso_cargofuncao,
        safe.parse_date('%d/%m/%Y', data_nomeacao_cargofuncao) as data_nomeacao_cargofuncao,
        safe.parse_date('%d/%m/%Y', data_ingresso_orgao) as data_ingresso_orgao,
        safe.parse_date('%d/%m/%Y', data_aposentadoria) as data_aposentadoria
    from source
)
select * from final