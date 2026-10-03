with fonte as(
    select * 
    from {{ ref('stg_enap__capacitacao') }}
),

com_sk as(
    select
        *,
        {{ dbt_utils.generate_surrogate_key(['codigo_pessoa', 'cod_curso', 'cod_turma', 'dt_matricula']) }} as sk_matricula
    from fonte   
),

final as(
    select
        sk_matricula,
        codigo_pessoa,
        cod_curso,
        year,
        month,
        concat(cast(year as string), '-', lpad(cast(month as string), 2, '0')) as ano_mes,
        cod_turma,
        nome_turma,
        case
            when sit_matricula = 'Concluida' then 'Concluído'
            when sit_matricula = 'Reprovado' then 'Não Aprovado'
            when sit_matricula in ('Desistente', 'Trancada', 'Não Concluído') then 'Evadido'
            else 'Não Informado'
        end as situacao_matricula,
        dt_matricula,
        dt_inicio,
        dt_fim,
        carga_horaria
    from com_sk
)

select * from final