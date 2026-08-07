with source as(
    select *
    from {{ source('siape', 'siape_afastamentos') }}
),

final as(
    select
        {{ dbt_utils.star(from=source('siape', 'siape_afastamentos'), except=['nome', 'data_inicio_afastamento', 'data_fim_afastamento']) }},
        safe.parse_date('%d/%m/%Y', data_inicio_afastamento) as data_inicio_afastamento,
        safe.parse_date('%d/%m/%Y', data_fim_afastamento) as data_fim_afastamento
    from source
)
select distinct * from final