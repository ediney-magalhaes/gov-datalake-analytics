with orgaos_reais as(
    select cod_org_lotacao, org_lotacao
    from {{ ref('stg_siape__ativos') }}
    union distinct
    select cod_org_lotacao, org_lotacao
    from {{ ref('stg_siape__aposentados') }}
),

org_sup_mais_recente as(
    select
        cod_org_lotacao,
        cod_orgsup_lotacao,
        orgsup_lotacao,
        row_number() over(partition by cod_org_lotacao order by year desc, month desc) as rn
    from {{ ref('stg_siape__ativos') }}
    qualify rn = 1
)

select
    o.cod_org_lotacao,
    o.org_lotacao,
    s.cod_orgsup_lotacao,
    s.orgsup_lotacao
from orgaos_reais o
left join org_sup_mais_recente s
    on o.cod_org_lotacao = s.cod_org_lotacao

