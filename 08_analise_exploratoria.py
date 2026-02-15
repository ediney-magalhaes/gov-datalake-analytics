from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import os

#Autenticação
caminho_chave = 'service_account.json'
ID_projeto = 'gov-datalake-analytics'
credencials = service_account.Credentials.from_service_account_file(caminho_chave)

#Concexão com cliente
client = bigquery.Client(credentials=credencials, project=credencials.project_id)

#query amostra da base
query = f"""
    SELECT * FROM `{ID_projeto}.bronze.siape_bruto`
    LIMIT 10000
"""

print("Baixando amostra de dados para análise")

#transforma a consulta em dataframe
df = client.query(query).to_dataframe()

#Relatório
print("\n--- Visão Geral (Tipo Dados)---")
print(df.info())

print("\n--- Contagem dos nulos (Onde está o buraco?)---")
print(df.isnull().sum())