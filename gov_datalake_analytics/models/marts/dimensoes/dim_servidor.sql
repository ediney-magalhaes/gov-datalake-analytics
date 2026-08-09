with servidores_reais as(
    select distinct id_servidor_portal, hash_cpf
    from {{ ref('stg_siape__ativos') }}
    where id_servidor_portal != '-11'
    union distinct
    select distinct id_servidor_portal, hash_cpf
    from {{ ref('stg_siape__aposentados') }}
    where id_servidor_portal != '-11'
),

nome_mais_recente as(
    select
        id_servidor_portal,
        nome,
        row_number() over(partition by id_servidor_portal order by year desc, month desc) as rn
    from {{ ref('stg_siape__ativos') }}
    qualify rn = 1
)

select s.id_servidor_portal, s.hash_cpf, n.nome, false as is_sigiloso
from servidores_reais s
left join nome_mais_recente n
    on s.id_servidor_portal = n.id_servidor_portal

union all

select
    '-11' as id_servidor_portal,
    null as hash_cpf,
    null as nome,
    true as is_sigiloso