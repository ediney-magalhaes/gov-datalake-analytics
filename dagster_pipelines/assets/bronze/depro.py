from dagster import asset, MonthlyPartitionsDefinition

from dagster_pipelines.resources.motor_ingestao import ingestao_bronze_raw_zip, normalizacao_da_bronze_raw

# Definição da partição mensal — de janeiro/2015 até o mês atual
particao_mensal = MonthlyPartitionsDefinition(start_date="2020-01-01")

# Asset: depro_alocacao
# O que faz: Baixa o registro de alocação dos servidores ativos do Portal da Transparência e salva como Parquet particionado por ano/mês
# Partição: Mensal (2020-01 até o mês atual)
# Fonte: ZIP público do Repositório de dados do governo
# Arquivo interno: alocacao-servidores.csv
# Separador: ; (padrão)
# Encoding: latin1 (padrão)
@asset(group_name="bronze_depro", partitions_def=particao_mensal)
def depro_alocacao(context):
    """Alocação de servidores por órgão — Bronze Raw e Normalized"""
    chave = context.partition_key
    ano = chave[:4]
    mes = chave[5:7]
    ingestao_bronze_raw_zip(
        sistema='depro_alocacao',
        ano=ano, mes=mes,
        url_download=f'https://repositorio.dados.gov.br/seges/raio-x/raiox-{ano}-{mes}.zip',
        nome_arquivo_interno='alocacao-servidores.csv'
    )
    normalizacao_da_bronze_raw(sistema='depro_alocacao', ano=ano, mes=mes)

# Asset: depro_cargos
# O que faz: Baixa o registro dos cargos dos servidores ativos do Portal da Transparência e salva como Parquet particionado por ano/mês
# Partição: Mensal (2015-01 até o mês atual)
# Fonte: ZIP público do Repositório de dados do governo
# Arquivo interno: cargos-efetivos.csv
# Separador: ; (padrão)
# Encoding: latin1 (padrão)
@asset(group_name="bronze_depro", partitions_def=particao_mensal)
def depro_cargos(context):
    """Cargos de servidores por órgão — Bronze Raw e Normalized"""
    chave = context.partition_key
    ano = chave[:4]
    mes = chave[5:7]
    ingestao_bronze_raw_zip(
        sistema='depro_cargos',
        ano=ano, mes=mes,
        url_download=f'https://repositorio.dados.gov.br/seges/raio-x/raiox-{ano}-{mes}.zip',
        nome_arquivo_interno='cargos-efetivos.csv'
    )
    normalizacao_da_bronze_raw(sistema='depro_cargos', ano=ano, mes=mes)

# Asset: depro_aposentadorias
# O que faz: Baixa o registro das aposentadorias dos servidores do Portal da Transparência e salva como Parquet particionado por ano/mês
# Partição: Mensal (2015-01 até o mês atual)
# Fonte: ZIP público do Repositório de dados do governo
# Arquivo interno: projecao-aposentadorias.csv
# Separador: ; (padrão)
# Encoding: latin1 (padrão)
@asset(group_name="bronze_depro", partitions_def=particao_mensal)
def depro_aposentadorias(context):
    """Projeção de aposentadorias por órgão — Bronze Raw e Normalized"""
    chave = context.partition_key
    ano = chave[:4]
    mes = chave[5:7]
    ingestao_bronze_raw_zip(
        sistema='depro_aposentadorias',
        ano=ano, mes=mes,
        url_download=f'https://repositorio.dados.gov.br/seges/raio-x/raiox-{ano}-{mes}.zip',
        nome_arquivo_interno='projecao-aposentadorias.csv'
    )
    normalizacao_da_bronze_raw(sistema='depro_aposentadorias', ano=ano, mes=mes)
