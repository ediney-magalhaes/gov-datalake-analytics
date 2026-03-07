import polars as pl
import os
import logging
import sys


#preparação do formatador do arquivo de log
formatador = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

#log do arquivo
arquivo_log = logging.FileHandler('historico_bronze_normalized.log', encoding='utf-8')

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

#função para normalização das bases
def normalizacao_da_bronze_raw(sistema, ano, mes):
    
    #defininfo local de leitura dos dados
    caminho_origem = f'data_lake_local/bronze_raw/{sistema}/year={ano}/month={mes}/part-000.parquet'
    
    #verificando existencia do arquivo
    if not os.path.exists(caminho_origem):
        logging.error("Arquivo não encontrado!")
        return
    #estabelecendo pasta de destino bronze_normalized
    caminho_destino_pasta = f'data_lake_local/bronze_normalized/{sistema}/year={ano}/month={mes}'
    
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

#normalizacao_da_bronze_raw('siape_ativos', '2025', '01')