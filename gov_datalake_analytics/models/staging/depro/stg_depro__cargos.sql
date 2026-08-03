with source as (
    select *
    from {{ source('depro', 'depro_cargos') }}
),

final as(
    select
        {{ dbt_utils.star(from=source('depro', 'depro_cargos'), except=['quantidade']) }},
        safe_cast(quantidade as int64) as quantidade
    from source
)
select * from final