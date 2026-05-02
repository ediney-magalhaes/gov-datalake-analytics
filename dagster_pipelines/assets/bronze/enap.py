from dagster import asset, MonthlyPartitionsDefinition
from dagster_pipelines.resources.motor_ingestao import ingestao_bronze_raw_zip, normalizacao_da_bronze_raw

# Definição da partição mensal — de janeiro/2015 até o mês atual
particao_mensal = MonthlyPartitionsDefinition(start_date="2015-01-01")

# Asset: enap_capacitacao
# O que faz: Baixa os dados de capacitação da Escola Virtual Gov e salva como Parquet particionado por ano/mês
# Partição: Mensal (2015-01 até o mês atual)
# Fonte: TAR.GZ público da Escola Virtual Gov (dupla compactação: TAR.GZ > TAR.GZ > CSV)
# Arquivo interno: {ano}_{mes}_escolavirtual_dadosabertos_matriculas_utf8.tar.gz > .csv
# Separador: | (pipe)
# Encoding: utf-8
@asset(group_name="bronze_enap", partitions_def=particao_mensal)
def enap_capacitacao(context):
    """Matrículas e capacitação de servidores — Escola Virtual Gov — Bronze Raw e Normalized"""
    chave = context.partition_key
    ano = chave[:4]
    mes = chave[5:]
    ingestao_bronze_raw_zip(
        sistema='enap_capacitacao',
        ano=ano, mes=mes,
        url_download=f'https://dadosaberto.evg.gov.br/ultimos_dozemeses/escolavirtual_dadosabertos_matriculas_ultimos_dozemeses_utf8.tar.gz',
        nome_arquivo_interno=[
            f'{ano}_{mes}_escolavirtual_dadosabertos_matriculas_utf8.tar.gz',
            f'{ano}_{mes}_escolavirtual_dadosabertos_matriculas_utf8.csv'
        ],
        separador='|',
        encoding='utf-8',
        formato_compactado='tar.gz'
    )
    normalizacao_da_bronze_raw(sistema='enap_capacitacao', ano=ano, mes=mes)