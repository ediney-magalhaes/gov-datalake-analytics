with remuneracao as(
    select *
    from {{ ref('stg_siape__remuneracao') }}
),

vinculo_contagem as(
    select
        id_servidor_portal,
        year,
        month,
        cod_org_lotacao,
        cod_tipo_vinculo,
        count(*) over(partition by id_servidor_portal, year, month) as qtde_vinculo_mes
    from {{ ref('stg_siape__ativos') }}
),

vinculo_contexto as(
    select
        id_servidor_portal,
        year,
        month,
        case when qtde_vinculo_mes > 1 then null else cod_org_lotacao end as cod_org_lotacao,
        case when qtde_vinculo_mes > 1 then null else cod_tipo_vinculo end as cod_tipo_vinculo
    from vinculo_contagem
),

vinculo_contexto_dedup as(
    select
        *,
        row_number() over(partition by id_servidor_portal, year, month order by id_servidor_portal) as rn
    from vinculo_contexto
    qualify rn = 1
),

enriquecido as(
    select
        {{ dbt_utils.star(from=ref('stg_siape__remuneracao'), relation_alias='r', except=["remuneracao_basica_bruta_dolar", "abate_teto_dolar", "gratificacao_natalina_dolar",
                                                                                          "abate_teto_gratificacao_natalina_dolar", "ferias_dolar", "outras_remuneracoes_eventuais_dolar",
                                                                                          "irrf_dolar", "pssrpgs_dolar", "demais_deducoes_dolar", "pensao_militar_dolar",
                                                                                          "fundo_saude_dolar", "taxa_ocupacao_imovel_funcional_dolar", "remuneracao_deducoes_obrigatorias_dolar",
                                                                                          "verbas_indenizatorias_pessoal_civil_dolar", "verbas_indenizatorias_pessoal_militar_dolar",
                                                                                          "verbas_indenizatorias_desligamento_voluntario_dolar", "total_verbas_indenizatorias_dolar",
                                                                                          "ano", "mes", "nome", "source_system", "ingestion_timestamp", "schema_version", "hash_cpf",
                                                                                          "id_servidor_portal", "year", "month"]) }},
        v.cod_org_lotacao,
        v.cod_tipo_vinculo,
        r.id_servidor_portal,
        r.year,
        r.month
    from remuneracao r
    left join vinculo_contexto_dedup v
        on r.id_servidor_portal = v.id_servidor_portal and r.year = v.year and r.month = v.month
)

select * from enriquecido
