with source as(
    select *
    from {{ source('depro', 'depro_alocacao') }}
),

final as(
    select
        {{ dbt_utils.star(from=source('depro', 'depro_alocacao'), except=['quantidade_servidores_cedidos_apf', 'quantidade_servidores_cedidos_outros',
                                                                          'quantidade_servidores_cedidos', 'quantidade_servidores_quadro_pessoal', 'quantidade_estagiarios']) }},
        safe_cast(quantidade_servidores_cedidos_apf as int64) as quantidade_servidores_cedidos_apf,
        safe_cast(quantidade_servidores_cedidos_outros as int64) as quantidade_servidores_cedidos_outros,
        safe_cast(quantidade_servidores_cedidos as int64) as quantidade_servidores_cedidos,
        safe_cast(quantidade_servidores_quadro_pessoal as int64) as quantidade_servidores_quadro_pessoal,
        safe_cast(quantidade_estagiarios as int64) as quantidade_estagiarios
    from source
)
select * from final