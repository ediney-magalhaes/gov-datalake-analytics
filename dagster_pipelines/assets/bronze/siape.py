from dagster import asset, MonthlyPartitionsDefinition

from dagster_pipelines.resources.motor_ingestao import ingestao_bronze_raw_zip, normalizacao_da_bronze_raw

# Definição da partição mensal — de janeiro/2015 até o mês atual
particao_mensal = MonthlyPartitionsDefinition(start_date="2015-01-01")

# Asset: siape_ativos
# O que faz: Baixa o cadastro de servidores ativos do Portal da Transparência, anonimiza CPF e salva como Parquet particionado por ano/mês
# Partição: Mensal (2015-01 até o mês atual)
# Fonte: ZIP público do Portal da Transparência
# Arquivo interno: {ano}{mes}_Cadastro.csv
# Separador: ; (padrão)
# Encoding: latin1 (padrão)
@asset(group_name="bronze_siape", partitions_def=particao_mensal)
def siape_ativos(context):
    """Cadastro de servidores ativos — Bronze Raw e Normalized"""
    import requests
    chave = context.partition_key
    ano = chave[:4]
    mes = chave[5:7]
    url = f'https://portaldatransparencia.gov.br/download-de-dados/servidores/{ano}{mes}_Servidores_SIAPE'
    ingestao_bronze_raw_zip(
        sistema='siape_ativos',
        ano=ano, mes=mes,
        url_download=url,
        nome_arquivo_interno=f'{ano}{mes}_Cadastro.csv'
    )
    normalizacao_da_bronze_raw(sistema='siape_ativos', ano=ano, mes=mes)
#@asset(group_name="bronze_siape", partitions_def=particao_mensal)
#def siape_ativos(context):
#    """Cadastro de servidores ativos — Bronze Raw e Normalized"""
#    chave = context.partition_key
#    ano = chave[:4]
#    mes = chave[5:7]
#    ingestao_bronze_raw_zip(
#        sistema='siape_ativos',
#        ano=ano, mes=mes,
#        url_download=f'https://portaldatransparencia.gov.br/download-de-dados/servidores/{ano}{mes}_Servidores_SIAPE',
#        nome_arquivo_interno=f'{ano}{mes}_Cadastro.csv'
#    )
#    normalizacao_da_bronze_raw(sistema='siape_ativos', ano=ano, mes=mes)

# Asset: siape_remuneracao
# O que faz: Baixa o registro de remunerações de servidores ativos do Portal da Transparência, anonimiza CPF e salva como Parquet particionado por ano/mês
# Partição: Mensal (2015-01 até o mês atual)
# Fonte: ZIP público do Portal da Transparência
# Arquivo interno: {ano}{mes}_Remuneracao.csv
# Separador: ; (padrão)
# Encoding: latin1 (padrão)
@asset(group_name="bronze_siape", partitions_def=particao_mensal)
def siape_remuneracao(context):
    """Remuneração de servidores ativos — Bronze Raw e Normalized"""
    chave = context.partition_key
    ano = chave[:4]
    mes = chave[5:7]
    ingestao_bronze_raw_zip(
        sistema='siape_remuneracao',
        ano=ano, mes=mes,
        url_download=f'https://portaldatransparencia.gov.br/download-de-dados/servidores/{ano}{mes}_Servidores_SIAPE',
        nome_arquivo_interno=f'{ano}{mes}_Remuneracao.csv'
    )
    normalizacao_da_bronze_raw(sistema='siape_remuneracao', ano=ano, mes=mes)

# Asset: siape_aposentados
# O que faz: Baixa o registro de servidores aposentados do Portal da Transparência, anonimiza CPF e salva como Parquet particionado por ano/mês
# Partição: Mensal (2015-01 até o mês atual)
# Fonte: ZIP público do Portal da Transparência
# Arquivo interno: {ano}{mes}_Cadastro.csv
# Separador: ; (padrão)
# Encoding: latin1 (padrão)
@asset(group_name="bronze_siape", partitions_def=particao_mensal)
def siape_aposentados(context):
    """Cadastro de aposentados e pensionistas — Bronze Raw e Normalized"""
    chave = context.partition_key
    ano = chave[:4]
    mes = chave[5:7]
    if int(ano) < 2020:
        url=f'https://portaldatransparencia.gov.br/download-de-dados/servidores/{ano}{mes}_Servidores_SIAPE'
    else:
        url=f'https://portaldatransparencia.gov.br/download-de-dados/servidores/{ano}{mes}_Aposentados_SIAPE'
    ingestao_bronze_raw_zip(
        sistema='siape_aposentados',
        ano=ano, mes=mes,
        url_download= url, 
        nome_arquivo_interno=f'{ano}{mes}_Cadastro.csv'
    )
    normalizacao_da_bronze_raw(sistema='siape_aposentados', ano=ano, mes=mes)

# Asset: siape_afastamentos
# O que faz: Baixa o cadastro de servidores afastados do Portal da Transparência, anonimiza CPF e salva como Parquet particionado por ano/mês
# Partição: Mensal (2015-01 até o mês atual)
# Fonte: ZIP público do Portal da Transparência
# Arquivo interno: {ano}{mes}_Afastamentos.csv
# Separador: ; (padrão)
# Encoding: latin1 (padrão)
@asset(group_name="bronze_siape", partitions_def=particao_mensal)
def siape_afastamentos(context):
    """Afastamentos de servidores ativos — Bronze Raw e Normalized"""
    chave = context.partition_key
    ano = chave[:4]
    mes = chave[5:7]
    ingestao_bronze_raw_zip(
        sistema='siape_afastamentos',
        ano=ano, mes=mes,
        url_download=f'https://portaldatransparencia.gov.br/download-de-dados/servidores/{ano}{mes}_Servidores_SIAPE',
        nome_arquivo_interno=f'{ano}{mes}_Afastamentos.csv'
    )
    normalizacao_da_bronze_raw(sistema='siape_afastamentos', ano=ano, mes=mes)