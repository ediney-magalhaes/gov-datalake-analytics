WITH source AS(
    SELECT * FROM {{source('bronze', 'remuneracao_ingestao_automatica')}}
),
renamed AS(
    SELECT
    CAST(CPF AS STRING) AS hash_cpf,
    CAST(MES_REFERENCIA AS STRING) AS mes_referencia,
    CAST(ID_SERVIDOR_PORTAL AS STRING) AS id_vinculo,
    COALESCE(CAST(REPLACE(REMUNERACAO_BASICA_BRUTA, ',', '.') AS NUMERIC), 0.00) AS remuneracao_bruta,
    COALESCE(CAST(REPLACE(REMUNERACAO_APOS_DEDUC_ES_OBRIGATORIAS, ',', '.') AS NUMERIC), 0.00) AS remuneracao_liquida,
    ROW_NUMBER() OVER(
        PARTITION BY CPF, ID_SERVIDOR_PORTAL, MES_REFERENCIA
        ORDER BY ID_SERVIDOR_PORTAL
    ) AS linha_numero
    FROM source
)
SELECT * FROM renamed WHERE linha_numero = 1