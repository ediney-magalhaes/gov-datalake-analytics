{{ config(
    materialized='table',
    alias='mart_servidores_remuneracao'
) }}

WITH ativos AS (
    SELECT * FROM {{ref('stg_siape_ativos')}}
),
remuneracao AS(
    SELECT * FROM {{ref('stg_siape_remuneracao')}}
),
cruzamento AS(
    SELECT
        ativos.*,
        remuneracao.remuneracao_bruta,
        remuneracao.remuneracao_liquida
    FROM ativos
    LEFT JOIN remuneracao
        ON ativos.hash_cpf = remuneracao.hash_cpf
        AND ativos.id_vinculo = remuneracao.id_vinculo
        AND ativos.mes_competencia = remuneracao.mes_referencia
)
SELECT * FROM cruzamento