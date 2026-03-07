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
arquivo_log = logging.FileHandler('pipeline_bronze_raw.log', encoding='utf-8')

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

#função de ingestão via api
def ingestao_bronze_raw_api(sistema, ano, mes, url_api, chave_autorizacao):

    #destino
    bucket_url = 'file:' + os.path.abspath('data_lake_local')
    destino = dlt.destinations.filesystem(bucket_url, layout=f"bronze_raw/{{table_name}}/year={ano}/month={mes}/{{load_id}}")

    #construindo pipeline de destino do dado
    pipeline = dlt.pipeline(pipeline_name=f'{sistema}' , destination= destino , dataset_name=f'bronze_{sistema}' )

    #conectando a base de dados
    @dlt.resource(nome=sistema, write_disposition='replace')
    def conectar_api():
        #url_api_siapecad = 'https://apigateway.conectagov.estaleiro.serpro.gov.br/api-consulta-siape/v1/consulta-siape'
        
        cabecalhos = {'Authorization': f'Bearer {chave_autorizacao}'}

        try:
            resposta = requests.get(url_api, headers= cabecalhos, verify=False, timeout=10)
            resposta.raise_for_status()
            dados_api = resposta.json()
            #injetar metadados linha a linha in-flight
            for linha in dados_api:
                linha['source_system'] = f'{sistema}'
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
    info_carga = pipeline.run(conectar_api(), loader_file_format='parquet')
    logging.info(f'Execução dlt finalizada {info_carga}')
