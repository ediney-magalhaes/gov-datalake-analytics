with source as(
    select *
    from {{ ref('stg_depro__aposentadorias') }}
),

agregado as(
    select
        orgao_codigo_siorg,
        year,
        month,
        ano_aposentadoria,
        faixa_etaria,
        natureza_juridica,
        escolaridade_cargo,
        plano_carreira,
        grupo_cargo,
        cargo,
        sexo,
        sum(quantidade_prevista) as quantidade_prevista,
        concat(cast(year as string), '-', lpad(cast(month as string), 2, '0')) as ano_mes
    from source
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
)

select * from agregado