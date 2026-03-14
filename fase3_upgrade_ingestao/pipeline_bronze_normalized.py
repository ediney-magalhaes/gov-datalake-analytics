import polars as pl
import os
import logging
import sys
import re
from datetime import datetime

# Garante que a pasta de logs exista para não sujar a raiz do projeto
os.makedirs('logs', exist_ok=True)

# preparação do formatador do arquivo de log
formatador = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# log do arquivo
arquivo_log = logging.FileHandler('logs/historico_bronze_normalized.log', encoding='utf-8')

# log da tela
tela_log = logging.StreamHandler(sys.stdout)

# chamando os logs
arquivo_log.setFormatter(formatador)
tela_log.setFormatter(formatador)

# definindo volume de logs
logging.getLogger().setLevel(logging.INFO)

# conectando os logs a definição de níveis
logging.getLogger().addHandler(arquivo_log)
logging.getLogger().addHandler(tela_log)


# Função auxiliar para garantir snake_case
def para_snake_case(texto):
    texto = str(texto).strip().lower()
    texto = re.sub(r'[^\w\s-]', '', texto) # remove pontuação/acentos
    texto = re.sub(r'[\s-]+', '_', texto)  # troca espaços e traços por underline
    return texto

# função para normalização das bases
def normalizacao_da_bronze_raw(sistema, ano, mes):
    
    # definindo local de leitura dos dados
    caminho_origem = f'data_lake_local/bronze_raw/{sistema}/year={ano}/month={mes}/part-000.parquet'
    
    # verificando existencia do arquivo
    if not os.path.exists(caminho_origem):
        logging.error(f"Arquivo não encontrado na origem: {caminho_origem}")
        return
        
    # estabelecendo pasta de destino bronze_normalized
    caminho_destino_pasta = f'data_lake_local/bronze_normalized/{sistema}/year={ano}/month={mes}'
    
    # lendo arquivo parquet
    df_normalizado = pl.read_parquet(caminho_origem)
    logging.info(f'Lendo arquivo na origem: {sistema} ({ano}/{mes})')
    
    # 1. Transformação do nome das colunas - snake_case
    mapeamento_colunas = {coluna: para_snake_case(coluna) for coluna in df_normalizado.columns}
    df_normalizado = df_normalizado.rename(mapeamento_colunas)
    logging.info('Colunas transformadas para snake_case com sucesso!')     
    
    # 2. Injeção de Metadados Universais (Arquitetura Fase 0)
    df_normalizado = df_normalizado.with_columns([
        pl.lit(sistema).alias('source_system'),
        pl.lit(datetime.now()).alias('ingestion_timestamp'),
        pl.lit('v1').alias('schema_version')
    ])
    logging.info('Metadados universais (source_system, ingestion_timestamp, schema_version) injetados!')
    
    # criando diretorio
    os.makedirs(caminho_destino_pasta, exist_ok=True)
    
    # salvando o arquivo
    df_normalizado.write_parquet(f'{caminho_destino_pasta}/part-000.parquet')
    logging.info(f'Arquivo salvo com sucesso em: {caminho_destino_pasta}')

# Teste local da função
#normalizacao_da_bronze_raw('depro_alocacao', '2025', '07')