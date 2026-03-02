import dlt
import requests
import logging
import sys

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

#construindo pipeline de destino do dado
pipeline_siapecad = dlt.pipeline(pipeline_name='siapecad' , destination='duckdb' , dataset_name='bronze_siapecad' )

#conectando a base de dados
@dlt.resource
def conectar_api_siapecad():
    url_api = 'https://api.servidor.gov.br/siapecad/v1/servidores'
    
    cabecalhos = {'Authorization': 'Bearer CHAVE_API'}

    resposta = requests.get(url_api, headers= cabecalhos, verify=False)
    
    yield resposta.json()

#executando pipeline
info_carga = pipeline_siapecad.run(conectar_api_siapecad())
logging.info(f'Execução dlt finalizada {info_carga}')
