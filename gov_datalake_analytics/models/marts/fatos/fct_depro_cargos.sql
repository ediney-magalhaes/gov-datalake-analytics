with source as(
    select *
    from {{ ref('stg_depro__cargos') }}
),

agregado as(
    select
        orgao_codigo_siorg,
        year,
        month,
        carreira,
        grupo_cargo,
        cargo,
        sum(quantidade) as quantidade,
        concat(cast(year as string), '-', lpad(cast(month as string), 2, '0')) as ano_mes
    from source
    group by 1, 2, 3, 4, 5, 6
)

select * from agregado