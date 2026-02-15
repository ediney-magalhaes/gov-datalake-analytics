from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import os

#Conexão
caminho_chave = 'service_account.json'
credencials = service_account.Credentials.from_service_account_file(caminho_chave)
client = bigquery.Client(credentials=credencials, project=credencials.project_id)

#Amostra de dados
query = """
    SELECT * FROM `gov-datalake-analytics.bronze.siape_bruto`
    LIMIT 10000;
"""
print('Baixando amostra de dados...')
df = client.query(query).to_dataframe()
print(f'Dados carregados {df.shape[0]} linhas e {df.shape[1]} colunas')


#Auditoria
resultados = []
 
for coluna in df.columns:
    n_nulos = df[coluna].isnull().sum()
    tipo_dado = df[coluna].dtype
    n_unicos = df[coluna].nunique()
    dicionario = {'Nome da coluna':coluna,
                  'Valores nulos':n_nulos,
                  'Valores únicos': n_unicos,
                  'Tipo dos dados':tipo_dado}
    resultados.append(dicionario)
print(resultados)

#Transformar em tabela
df_auditoria = pd.DataFrame(resultados)

#ordenação
df_auditoria = df_auditoria.sort_values(by='Valores únicos')

print(df_auditoria.to_string())

# Vamos ver O QUE tem dentro dessa coluna de valor único
print("\n--- O MISTÉRIO DA DATA ÚNICA ---")
print(f"O valor repetido em DATA_NOMEACAO é: {df['DATA_NOMEACAO_CARGOFUNCAO'].unique()}")
print(f"O valor repetido em DATA_INICIO_AFASTAMENTO é: {df['DATA_INICIO_AFASTAMENTO'].unique()}")