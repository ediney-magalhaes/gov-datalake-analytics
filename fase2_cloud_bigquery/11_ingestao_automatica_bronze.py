import requests
import zipfile
import io
import pandas as pd
import hashlib
import logging
from google.cloud import bigquery
from google.oauth2 import service_account
import os

logging.basicConfig(filename='auditoria_bronze.log', level=logging.INFO, format='%(asctime)s - %(message)s')

#
meses_carga = ['202509', '202510', '202511']
url_siape = 'https://portaldatransparencia.gov.br/download-de-dados/servidores/{}_Servidores_SIAPE'

logging.info('Iniciando Robô de Ingestão da Camada Bronze...')

#caminho dos arquivos
arquivo_json = 'service_account.json'
arquivo_ID_projeto = 'gov-datalake-analytics'

#nova tentativa de envio ao BigQuery
tabela_destino = f'{arquivo_ID_projeto}.bronze.siape_ingestao_automatica'

#autenticação
credencials = service_account.Credentials.from_service_account_file(arquivo_json)

client = bigquery.Client(credentials=credencials, project=arquivo_ID_projeto)
print('Cliente conectado com sucesso!')

#Loop de download
for indice, mes in enumerate(meses_carga):
    url = url_siape.format(mes)
    logging.info(f'\n Baixando dados de {mes}...')
    #Fazendo a requisição no servidor do governo
    resposta = requests.get(url, verify=False)

    #Tratamento de erro
    if resposta.status_code == 200:
        logging.info(f'Download concluído (Status 200). Extraindo na memória...')
        #transformando a resposta da internet em um arquivo na memória
        arquivo_zip_memoria = io.BytesIO(resposta.content)
        #Abre o zip
        with zipfile.ZipFile(arquivo_zip_memoria) as z:
            #Usar o primeiro arquivo dentro do zip
            arquivos_do_zip = z.namelist()
            nome_arquivo_csv = [arq for arq in arquivos_do_zip if 'Cadastro.csv' in arq][0]
            logging.info(f'Arquivo correto encontrado no dentro do ZIP: {nome_arquivo_csv}')
            
            #Pandas lê o csv direto no zip
            with z.open(nome_arquivo_csv) as f:
                df_mes = pd.read_csv(f, sep=';', encoding='latin1', dtype=str)
                df_mes['CPF'] = df_mes['CPF'].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest())
                #guarda o mes referencia
                df_mes['MES_REFERENCIA'] = mes
                # ... (suas linhas de Hash de CPF e MES_REFERENCIA ficam aqui) ...
                
                logging.info(f"Preparando envio do mês {mes} ({len(df_mes)} linhas)...")
                
                # Regra de Inserção: O primeiro mês (índice 0) recria a tabela. Os outros adicionam.
                if indice == 0:
                    modo_escrita = 'WRITE_TRUNCATE'
                else:
                    modo_escrita = 'WRITE_APPEND'
                    
                job_config = bigquery.LoadJobConfig(write_disposition=modo_escrita)
                
                # Envia o df_mes atual para o BigQuery
                job = client.load_table_from_dataframe(df_mes, tabela_destino, job_config=job_config)
                job.result() # Espera o upload terminar
                
                logging.info(f"✅ Mês {mes} carregado no BigQuery com sucesso!")
                
                # O Truque de Mestre: Apaga o DataFrame da memória RAM para não explodir o PC
                del df_mes
    elif resposta.status_code == 404:
        logging.info(f'Erro 404: os dados de {mes} ainda não existem no portal.')
    else:
        logging.info(f'Erro desconhecido: Status {resposta.status_code}')