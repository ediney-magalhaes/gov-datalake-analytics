WITH source AS (
    SELECT * FROM {{source('bronze', 'siape_ingestao_automatica')}}
),
renamed AS (
    SELECT
    CAST(Id_SERVIDOR_PORTAL AS STRING) AS id_vinculo, --transforma a coluna Id_SERVIDOR_PORTAL EM UMA string
    CAST(CPF AS STRING) AS hash_cpf, --transforma a coluna CPF em uma string
    CAST(MES_REFERENCIA AS STRING) AS mes_competencia, --transforma a coluna MES_REFERENCIA em uma string
    TRIM(NOME) AS nome_servidor, --remove os espaços da coluna NOME
    TRIM(ORG_LOTACAO) AS orgao_lotacao, --remove os espaços da coluna ORG_LOTACAO
    TRIM(DESCRICAO_CARGO) AS cargo, --remove os espaços da coluna DESCRICAO_CARGO
    CAST(UF_EXERCICIO AS STRING) AS uf_exercicio, --transforma a coluna UF_EXERCICIO em uma string
    CAST(SITUACAO_VINCULO AS STRING) AS situacao_vinculo, --transforma a coluna SITUACAO_VINCULO em uma string
    CAST(REGIME_JURIDICO AS STRING) AS regime_juridico, --transforma a coluna REGIME_JURIDICO em uma string
    CAST(DATA_INGRESSO_ORGAO AS STRING) AS data_ingresso, --transforma a coluna DATA_INGRESSO_ORGAO em uma string
    ROW_NUMBER () OVER(
        PARTITION BY CPF, MES_REFERENCIA, Id_SERVIDOR_PORTAL
        ORDER BY NOME
    ) AS linha_numero
    FROM source
)
SELECT * FROM renamed WHERE linha_numero = 1