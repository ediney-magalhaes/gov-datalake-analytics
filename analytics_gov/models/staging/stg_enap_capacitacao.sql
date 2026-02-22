WITH source AS (
    SELECT * FROM {{source('bronze', 'enap_ingestao_automatica')}}
),
renamed AS(
    SELECT
    CAST(HASH_CPF_ORIGEM AS STRING) AS hash_cpf, -- transforma da coluna HASH_CPF_ORIGEM em String
    COALESCE(CAST(cod_curso AS STRING), 'NAO_INFORMADO') AS id_curso, -- transforma da coluna cod_curso em String
    CAST(carga_horaria AS STRING) AS carga_horaria, -- transforma da coluna carga_horaria em String
    CAST(dt_matricula AS STRING) AS data_matricula, -- transforma da coluna dt_matricula em String
    TRIM(sit_matricula) AS situacao_matricula, -- remove os espaços da coluna sit_matricula
    TRIM(nome_curso) AS nome_curso, -- remove os espaços da coluna nome_curso
    TRIM(tematica) AS tematica_curso, -- remove os espaços da coluna tematica
    ROW_NUMBER () OVER(
        PARTITION BY HASH_CPF_ORIGEM, cod_curso, dt_matricula
        ORDER BY nome_curso
    ) AS linha_numero
    FROM source
)
SELECT * FROM renamed WHERE linha_numero = 1
