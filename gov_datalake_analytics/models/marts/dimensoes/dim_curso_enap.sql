with cursos_reais as(
    select distinct
        cod_curso,
        modalidade_turma
    from {{ ref('stg_enap__capacitacao') }}
),

atributos_mais_recentes as(
    select
        cod_curso,
        nome_curso,
        conteudista,
        tematica,
        row_number() over(partition by cod_curso order by dt_matricula desc) as rn
    from {{ ref('stg_enap__capacitacao') }}
    qualify rn = 1
)

select
    cr.cod_curso,
    cr.modalidade_turma,
    ar.nome_curso,
    ar.conteudista,
    ar.tematica
from cursos_reais cr
left join atributos_mais_recentes ar
    on cr.cod_curso = ar.cod_curso