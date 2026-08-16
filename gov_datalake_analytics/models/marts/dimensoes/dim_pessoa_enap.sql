with pessoas_reais as(
    select distinct
        codigo_pessoa,
        nacionalidade
    from {{ ref('stg_enap__capacitacao') }}
),

atributos_mais_recentes as(
    select
        codigo_pessoa,
        raca,
        sexo,
        deficiencia,
        uf_pessoa,
        municipio_pessoa,
        instituicao,
        poder,
        esfera,
        row_number() over(partition by codigo_pessoa order by dt_matricula desc) as rn
    from {{ ref('stg_enap__capacitacao') }}
    qualify rn = 1
)

select
    pr.codigo_pessoa,
    pr.nacionalidade,
    ar.raca,
    ar.sexo,
    ar.deficiencia,
    ar.uf_pessoa,
    ar.municipio_pessoa,
    ar.instituicao,
    ar.poder,
    ar.esfera
from pessoas_reais pr
left join atributos_mais_recentes ar
    on pr.codigo_pessoa = ar.codigo_pessoa