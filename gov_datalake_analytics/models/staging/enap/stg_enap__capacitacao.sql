with source as(
    select *
    from {{ source('enap', 'enap_capacitacao') }}
),

final as(
    select
        {{ dbt_utils.star(from=source('enap', 'enap_capacitacao'), except=['dt_matricula', 'dt_inicio', 'dt_fim', 'dt_inicio_insc', 'dt_fim_insc', 'idade', 'carga_horaria']) }},
        safe.parse_datetime('%Y-%m-%d %H:%M:%S', dt_matricula) as dt_matricula,
        safe.parse_datetime('%Y-%m-%d %H:%M:%S', dt_inicio) as dt_inicio,
        safe.parse_datetime('%Y-%m-%d %H:%M:%S', dt_fim) as dt_fim,
        safe.parse_date('%Y-%m-%d', dt_inicio_insc) as dt_inicio_inscricao,
        safe.parse_date('%Y-%m-%d', dt_fim_insc) as dt_fim_inscricao,
        safe_cast(idade as int64) as idade,
        safe_cast(carga_horaria as int64) as carga_horaria
    from source
)
select * from final