{{ config(
    materialized='table',
    alias='mart_servidores_capacitacao'
) }}

WITH capacitacao AS (
    SELECT 
        hash_cpf,
        carga_horaria,
        tematica_curso,
        situacao_matricula
    FROM {{ ref('stg_enap_capacitacao') }}
),

servidores_ativos AS (
    SELECT 
        hash_cpf,
        cargo,
        situacao_vinculo,
        uf_exercicio
    FROM {{ ref('stg_siape_ativos') }}
),

cruzamento_ouro AS (
    SELECT 
        capacitacao.hash_cpf,
        capacitacao.carga_horaria,
        COALESCE(capacitacao.tematica_curso, 'Não Informado') as tematica_curso,
        CASE 
            WHEN capacitacao.situacao_matricula = 'Concluida' THEN 'Concluído'
            WHEN capacitacao.situacao_matricula IN ('Desistente', 'Trancada', 'Não Concluído', 'Reprovado') THEN 'Evadido'
            ELSE 'Não Informado'
        END AS situacao_matricula,
        servidores_ativos.cargo,
        servidores_ativos.situacao_vinculo,
        servidores_ativos.uf_exercicio
    FROM capacitacao
    LEFT JOIN servidores_ativos 
        ON capacitacao.hash_cpf = servidores_ativos.hash_cpf
)

SELECT * FROM cruzamento_ouro