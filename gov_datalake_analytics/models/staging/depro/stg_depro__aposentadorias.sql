with source as(
    select *
    from {{ source('depro', 'depro_aposentadorias') }}
),

final as(
    select
        {{ dbt_utils.star(from=source('depro', 'depro_aposentadorias'), except=['ano_aposentadoria', 'quantidade_prevista']) }},
        safe_cast(ano_aposentadoria as int64) as ano_aposentadoria,
        safe_cast(quantidade_prevista as int64) as quantidade_prevista
    from source
)
select * from final