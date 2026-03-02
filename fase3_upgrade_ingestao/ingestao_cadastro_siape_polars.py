import io
import requests
import zipfile
import polars as pl
import logging
import sys
import hashlib

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

#definindo caminho para acessar os dados
periodo = '202501'
url = f'https://portaldatransparencia.gov.br/download-de-dados/servidores/{periodo}_Servidores_SIAPE'

#obtendo retorno da url em bytes
logging.info(f'Iniciando o download dos dados do SIAPE para o periodo {periodo}')
resposta = requests.get(url, verify=False)
arquivo_zip = io.BytesIO(resposta.content)

#abrindo o arquivo zip
with zipfile.ZipFile(arquivo_zip) as z:
    nome_csv = f'{periodo}_Cadastro.csv'

    #extraindo o arquivo
    arquivo_extraido = z.open(nome_csv)

    #lendo o arquivo com o Polars
    df_cadastro = pl.read_csv(arquivo_extraido.read(), separator=';', encoding='latin1')
    logging.info(f'Arquivo lido com sucesso pelo Polars. {df_cadastro.height} linhas encontradas.')

    #sobrescrevendo a coluna de CPF aplicando SHA-256
    df_cadastro = df_cadastro.with_columns(
        pl.col('CPF').map_elements(lambda x: hashlib.sha256(str(x).encode('utf-8')).hexdigest(), return_dtype=pl.String)
    )
    logging.info('Anonimizacao aplicada com sucesso na coluna CPF!')

    #salvando o arquivo
    df_cadastro.write_parquet(f'{periodo}_cadastro_siape_anonimizado.parquet')
    logging.info('Arquivo salvo com sucesso!')

print(df_cadastro.head())