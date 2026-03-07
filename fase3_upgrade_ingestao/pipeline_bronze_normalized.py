import polars as pl
import os
import logging
import sys


#preparação do formatador do arquivo de log
formatador = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

#log do arquivo
arquivo_log = logging.FileHandler('historico_siape.log', encoding='utf-8')

#log da tela
tela_log = logging.StreamHandler(sys.stdout)

#chamando os logs
arquivo_log.setFormatter(formatador)
tela_log.setFormatter(formatador)

#definindo volume de logs
logging.getLogger().setLevel(logging.INFO)

#conectando os logs a definição de níveis
logging.getLogger().addHandler(arquivo_log)
logging.getLogger().addHandler(tela_log)

#defininfo local de leitura dos dados
caminho_origem = 'data_lake_local/bronze_raw/siape_ativos/year=2025/month=01/part-000.parquet'

#estabelecendo pasta de destino bronze_normalized
caminho_destino_pasta = 'data_lake_local/bronze_normalized/siape_ativos/year=2025/month=01'

#lendo arquivo parquet
df_normalizado = pl.read_parquet(caminho_origem)
logging.info('Lendo arquivo na origem...')

#transformação do nome das colunas - snake_case
mapeamento_colunas = {coluna: coluna.lower() for coluna in df_normalizado.columns}
df_normalizado = df_normalizado.rename(mapeamento_colunas)
logging.info('Colunas transformadas (snake_case) com sucesso!')

#criando diretorio
os.makedirs(caminho_destino_pasta, exist_ok=True)
#salvando o arquivo
df_normalizado.write_parquet(f'{caminho_destino_pasta}/part-000.parquet')
logging.info('Arquivo salvo com sucesso!')