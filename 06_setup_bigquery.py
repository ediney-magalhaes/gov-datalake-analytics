from google.cloud import bigquery
from google.oauth2 import service_account
import os

arquivo_json = 'service_account.json'
arquivo_ID_projeto = 'gov-datalake-analytics'

#autenticação
credencials = service_account.Credentials.from_service_account_file(arquivo_json)

client = bigquery.Client(credentials=credencials, project=arquivo_ID_projeto)
print('Cliente conectado com sucesso!')

#lista de camadas
lista_datasets = ['bronze', 'prata', 'ouro']

for nome in lista_datasets:
    dataset_id = f'{arquivo_ID_projeto}.{nome}'
    print(f'preparando para criar {dataset_id}')

    dataset_obj = bigquery.Dataset(dataset_id)
    dataset_obj.location = 'US'

    try:
        client.create_dataset(dataset_obj, timeout=30)
        print(f"Sucesso! Dataset '{nome}'criado com sucesso.")
    except Exception as e:
        print(f'Aviso {nome} já existe ou deu erro {e}')

print('Fim do processo!')