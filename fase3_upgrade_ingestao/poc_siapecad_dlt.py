import dlt
import requests
import logging
import sys
import os
import hashlib

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
salt = os.getenv('HASH_SALT')

#preparação do formatador do arquivo de log
formatador = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

#log do arquivo
arquivo_log = logging.FileHandler('historico_siapecad.log', encoding='utf-8')

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

#destino
bucket_url = 'file:' + os.path.abspath('data_lake_local')
destino = dlt.destinations.filesystem(bucket_url, layout="bronze_raw/{table_name}/year=2026/month=03/{load_id}")

#construindo pipeline de destino do dado
pipeline_siapecad = dlt.pipeline(pipeline_name='siapecad' , destination= destino , dataset_name='bronze_siapecad' )

#conectando a base de dados
@dlt.resource(write_disposition='replace')
def conectar_api_siapecad():
    url_api = 'https://apigateway.conectagov.estaleiro.serpro.gov.br/api-consulta-siape/v1/consulta-siape'
    
    cabecalhos = {'Authorization': 'Bearer CHAVE_API'}

    try:
        resposta = requests.get(url_api, headers= cabecalhos, verify=False, timeout=10)
        resposta.raise_for_status()
        dados_api = resposta.json()
        #injetar metadados linha a linha in-flight
        for linha in dados_api:
            linha['source_system'] = 'siape_cad'
            linha['ingestion_timestamp'] = datetime.now().isoformat()

            #caso haja coluna CPF faz hash com salt
            if 'cpf' in linha:
                linha['hash_cpf'] = hashlib.sha256((str(linha['cpf']) + str(salt)).encode('utf-8')).hexdigest()
                #deleta cpf original por segurança
                del linha['cpf']
        yield dados_api
    except requests.exceptions.RequestException as erro:
        logging.error(f'O tempo de conexão falhou: {erro}')
        yield []

#executando pipeline
info_carga = pipeline_siapecad.run(conectar_api_siapecad(), loader_file_format='parquet')
logging.info(f'Execução dlt finalizada {info_carga}')
