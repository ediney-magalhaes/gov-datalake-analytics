with source as(
    select *
    from {{ ref('stg_depro__alocacao') }}
),

agregado as(
    select
        orgao_codigo_siorg,
        year,
        month,
        sum(quantidade_servidores_cedidos_apf) as qtd_servidores_cedidos_apf,
        sum(quantidade_servidores_cedidos_outros) as qtd_servidores_cedidos_outros,
        sum(quantidade_servidores_cedidos) as qtd_servidores_cedidos,
        sum(quantidade_servidores_quadro_pessoal) as qtd_servidores_quadro_pessoal,
        sum(quantidade_estagiarios) as qtd_estagiarios,
        concat(cast(year as string), '-',  lpad(cast(month as string), 2, '0')) as ano_mes
    from source
    group by 1, 2, 3
)

select * from agregado