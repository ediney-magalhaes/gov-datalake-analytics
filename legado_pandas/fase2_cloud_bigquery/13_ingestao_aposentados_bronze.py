import requests
import zipfile
import io
import pandas as pd
import hashlib
import logging
from google.cloud import bigquery
from google.oauth2 import service_account
import time

#arquivo de log
logging.basicConfig(filename='auditoria_bronze.log', level=logging.INFO, format='%(asctime)s - %(message)s')
logging.info('--------------------------------------------------')
logging.info('Iniciando Robô de Ingestão: APOSENTADOS (Camada Bronze)...')

# Mapeamento do ano de 2025 inteiro (para garantir cruzamento exato com a base da ENAP)
meses_carga = ['202501', '202502', '202503', '202504', '202505', '202506', '202507', '202508', '202509', '202510', '202511', '202512']

# URL oficial da API do Portal da Transparência para Aposentados e Pensionistas
url_aposentados = 'https://portaldatransparencia.gov.br/download-de-dados/servidores/{}_Aposentados_SIAPE'

# Caminhos e credenciais do projeto
arquivo_json = 'service_account.json'
arquivo_ID_projeto = 'gov-datalake-analytics'

# Nova tabela exclusiva na camada Bronze
tabela_destino = f'{arquivo_ID_projeto}.bronze.aposentados_ingestao_automatica'

# Autenticação e conexão com a nuvem do Google
credencials = service_account.Credentials.from_service_account_file(arquivo_json)
client = bigquery.Client(credentials=credencials, project=arquivo_ID_projeto)

logging.info('✅ Conexão com o Google BigQuery estabelecida com sucesso!')

# Dispara o cronômetro antes de começar a baixar/processar a base
tempo_inicio = time.time()
total_linhas_processadas = 0 # Contador de performance

try:
    for indice, mes in enumerate(meses_carga):
        url = url_aposentados.format(mes)
        logging.info(f'\n Baixando dados de {mes}...')
        # O "Disfarce Completo" imitando exatamente um Google Chrome no Windows
        cabecalho = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Connection': 'keep-alive'
        }
        
        # Fazendo a requisição com o disfarce completo e baixando em modo stream (conta-gotas)
        retorno = requests.get(url, verify=False, headers=cabecalho, stream=True, timeout=120)
        if retorno.status_code == 200:
            arquivo_zip_memoria = io.BytesIO(retorno.content)
            with zipfile.ZipFile(arquivo_zip_memoria) as z:
                arquivo_zip = z.namelist()
                nome_arquivo_csv = [arq for arq in arquivo_zip if 'Cadastro.csv' in arq][0]

                with z.open(nome_arquivo_csv) as f:
                    df_mes = pd.read_csv(f, sep=';', encoding='latin1', dtype=str)
                    df_mes['CPF'] = df_mes['CPF'].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest())
                    df_mes['MES_REFERENCIA'] = mes
                    if indice == 0:
                        modo_escrita = 'WRITE_TRUNCATE'
                    elif indice > 0:
                        modo_escrita = 'WRITE_APPEND'
                    total_linhas_processadas += len(df_mes)

                    job_config = bigquery.LoadJobConfig(write_disposition=modo_escrita)

                    # Envia o df_mes atual para o BigQuery
                    job = client.load_table_from_dataframe(df_mes, tabela_destino, job_config=job_config)
                    job.result() # Espera o upload terminar
                    #limpa a memória RAM assim que o mês é entregue no BigQuery
                    del df_mes
        elif retorno.status_code == 404:
            logging.info(f'Mês {mes} ainda não encontrado no portal (Erro 404). Pulando...')
        else:
            logging.info(f'Erro desconhecido no mês {mes}: Status {retorno.status_code}')

    # === Matemática do Tempo de Execução (Fim do Robô) ===
    tempo_fim = time.time() # Desliga o cronômetro
    duracao_segundos = tempo_fim - tempo_inicio
    
    if duracao_segundos > 0:
        velocidade = total_linhas_processadas / duracao_segundos
    else:
        velocidade = 0    
        
    logging.info(f"✅ Carga da base de APOSENTADOS concluída com sucesso!")
    logging.info(f'Total de linhas processadas: {total_linhas_processadas}')
    logging.info(f'Tempo de execução: {duracao_segundos:.2f} segundos')
    logging.info(f'Performance: {velocidade:.2f} linhas por segundo')
    logging.info('--------------------------------------------------')
except Exception as e:
    logging.error(f'log de erro fatal durante a execução: {e}')