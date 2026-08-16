with orgaos_reais as(
    select distinct orgao_codigo_siorg
    from {{ ref('stg_depro__cargos') }}
    union distinct
    select distinct orgao_codigo_siorg
    from {{ ref('stg_depro__aposentadorias') }}
    union distinct
    select distinct orgao_codigo_siorg
    from {{ ref('stg_depro__alocacao') }}
),

atributos_mais_recentes as(
    select
        orgao_codigo_siorg,
        orgao_nome,
        orgao_sigla,
        orgao_como_no_raiox_nome,
        orgao_como_no_raiox_sigla,
        orgao_superior_codigo_siorg,
        orgao_superior_nome,
        orgao_superior_sigla,
        row_number() over(partition by orgao_codigo_siorg order by year desc, month desc) as rn
    from {{ ref('stg_depro__cargos') }}
    qualify rn = 1
)

select
    og.orgao_codigo_siorg,
    ar.orgao_nome,
    ar.orgao_sigla,
    ar.orgao_como_no_raiox_nome,
    ar.orgao_como_no_raiox_sigla,
    ar.orgao_superior_codigo_siorg,
    ar.orgao_superior_nome,
    ar.orgao_superior_sigla
from orgaos_reais og
left join atributos_mais_recentes ar
    on og.orgao_codigo_siorg = ar.orgao_codigo_siorg