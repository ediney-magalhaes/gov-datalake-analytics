WITH source AS (
    SELECT * FROM {{ source('bronze','aposentados_ingestao_automatica') }}
),

renamed AS (
    SELECT
    CAST(ID_SERVIDOR_PORTAL AS STRING) AS id_vinculo,
    CAST(cpf AS STRING) AS hash_cpf,
    CAST(mes_referencia AS STRING) AS mes_competencia,
    TRIM(nome) AS nome_servidor,
    TRIM(ORG_LOTACAO) AS orgao_lotacao,
    ROW_NUMBER() OVER(
        PARTITION BY cpf, mes_referencia, ID_SERVIDOR_PORTAL
        ORDER BY nome
    ) AS linha_numero
    FROM source
)

SELECT * FROM renamed WHERE linha_numero = 1