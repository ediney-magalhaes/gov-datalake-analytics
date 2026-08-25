with fonte as (
    select
        id_servidor_portal,
        year,
        month,
        concat(cast(year as string), '-', lpad(cast(month as string), 2, '0')) as ano_mes,
        data_inicio_afastamento,
        data_fim_afastamento
    from {{ ref('stg_siape__afastamentos') }}
    where data_inicio_afastamento is not null or data_fim_afastamento is not null
)

select * from fonte