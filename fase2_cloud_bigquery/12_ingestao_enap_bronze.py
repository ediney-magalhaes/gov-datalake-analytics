import requests
import zipfile
import io
import pandas as pd
import hashlib
import logging
from google.cloud import bigquery
from google.oauth2 import service_account
import os
import tarfile

logging.basicConfig(filename='auditoria_bronze.log', level=logging.INFO, format='%(asctime)s - %(message)s')

#
url_enap = 'https://dadosaberto.evg.gov.br/ultimos_dozemeses/escolavirtual_dadosabertos_matriculas_ultimos_dozemeses_utf8.tar.gz'

logging.info('Iniciando Robô de Ingestão da Camada Bronze...')

#caminho dos arquivos
arquivo_json = 'service_account.json'
arquivo_ID_projeto = 'gov-datalake-analytics'

#nova tentativa de envio ao BigQuery
tabela_destino = f'{arquivo_ID_projeto}.bronze.enap_ingestao_automatica'

#autenticação
credencials = service_account.Credentials.from_service_account_file(arquivo_json)

client = bigquery.Client(credentials=credencials, project=arquivo_ID_projeto)
print('Cliente conectado com sucesso!')

logging.info('Baixando base consolidada do ENAP...')
resposta = requests.get(url_enap, verify=False, stream=True)

if resposta.status_code == 200:
    #Transforma a resposta da internet num "arquivo" na memória RAM
    arquivo_tar_memoria = io.BytesIO(resposta.content)
    #Abre o pacote TAR
    with tarfile.open(fileobj=arquivo_tar_memoria, mode='r:gz') as tar:
        #Pega o primeiro arquivo que está lá dentro (que deve ser o CSV) e extrai esse arquivo para o Pandas conseguir ler
        f = tar.extractfile(tar.getmembers()[0])
        logging.info(f'Arquivo encontrado: {tar.getmembers()[0].name}')
        
        df_enap = pd.read_csv(f, sep='|', encoding='utf-8', dtype=str, compression='gzip')

        logging.info(f'Dados lidos com sucesso! {len(df_enap)} linhas encontradas.')
        #print(df_enap.head())

        df_enap = df_enap.rename(columns={df_enap.columns[0]: 'HASH_CPF_ORIGEM'})
        
        #aplicando codificação no CPF
        df_enap['HASH_CPF_ORIGEM'] = df_enap['HASH_CPF_ORIGEM'].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest())

        job_config = bigquery.LoadJobConfig(write_disposition='WRITE_TRUNCATE')
        
        # Envia o dataframe para o BigQuery
        job = client.load_table_from_dataframe(df_enap, tabela_destino, job_config=job_config)
        job.result() # Espera o upload terminar
        logging.info(f"✅ Dataframe carregado no BigQuery com sucesso!")
        
        #Apaga o DataFrame da memória RAM para não explodir o PC
        del df_enap

