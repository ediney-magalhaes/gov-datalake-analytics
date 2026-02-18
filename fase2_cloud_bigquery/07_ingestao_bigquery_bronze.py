from google.cloud import bigquery
from google.oauth2 import service_account
import os

arquivo_json = 'service_account.json'
arquivo_ID_projeto = 'gov-datalake-analytics'

credencials = service_account.Credentials.from_service_account_file(arquivo_json)

client = bigquery.Client(credentials=credencials, project=arquivo_ID_projeto)
print('Cliente conectado com sucesso!')

arquivo_csv = 'cadastro_siape_bruto.csv'
ID_tabela_bronze = f'{arquivo_ID_projeto}.bronze.siape_bruto'

#configuração de envio
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True,
    write_disposition='WRITE_TRUNCATE',
    field_delimiter=';',
    encoding='ISO-8859-1',
    quote_character='"'
)

#abrir e enviar o arquivo
with open(arquivo_csv, 'rb') as source_file:
    print('Iniciando upload...')

    #carga
    job=client.load_table_from_file(source_file, ID_tabela_bronze, job_config=job_config)
    #espera finalizar
    job.result()
print('Carga finalizada!')