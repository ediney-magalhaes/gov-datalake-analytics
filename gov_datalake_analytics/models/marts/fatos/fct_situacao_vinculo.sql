with fonte as(
    select *
    from {{ ref('stg_siape__aposentados') }}
    where id_servidor_portal != '-11'
),

com_sk as(
    select
        *,
        {{ dbt_utils.generate_surrogate_key(['id_servidor_portal', 'year', 'month', 'cod_tipo_vinculo', 'situacao_vinculo', 'matricula', 'cod_org_lotacao']) }} as sk_situacao_vinculo
    from fonte
),

final as(
    select
        sk_situacao_vinculo,
        id_servidor_portal,
        year,
        month,
        concat(cast(year as string), '-', lpad(cast(month as string), 2, '0')) as ano_mes,
        cod_tipo_vinculo,
        situacao_vinculo,
        matricula,
        cod_org_lotacao,
        descricao_cargo,
        tipo_vinculo,
        tipo_aposentadoria,
        cod_tipo_aposentadoria,
        regime_juridico,
        data_aposentadoria
    from com_sk
)

select * from final