with fonte as(
    select *
    from {{ ref('stg_siape__ativos') }}
    where id_servidor_portal != '-11'
),

com_sk as(
    select
        *,
        {{ dbt_utils.generate_surrogate_key(['id_servidor_portal', 'year', 'month', 'cod_org_lotacao', 'cod_tipo_vinculo', 'matricula', 'situacao_vinculo', 'cod_uorg_exercicio']) }} as sk_vinculo
    from fonte
),

final as(
    select
        sk_vinculo,
        id_servidor_portal,
        year,
        month,
        concat(cast(year as string), '-', lpad(cast(month as string), 2, '0')) as ano_mes,
        cod_tipo_vinculo,
        cod_org_lotacao,
        matricula,
        situacao_vinculo,
        descricao_cargo,
        classe_cargo,
        nivel_cargo,
        sigla_funcao,
        nivel_funcao,
        funcao,
        regime_juridico,
        jornada_de_trabalho,
        cod_uorg_exercicio,
        uorg_exercicio,
        cod_org_exercicio,
        org_exercicio,
        uf_exercicio,
        data_ingresso_cargofuncao,
        data_ingresso_orgao
    from com_sk
)

select * from final