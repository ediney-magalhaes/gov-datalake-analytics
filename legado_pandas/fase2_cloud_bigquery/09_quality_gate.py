from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import os

# --- 1. CONEXÃO ---
caminho_chave = 'service_account.json'
credentials = service_account.Credentials.from_service_account_file(caminho_chave)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# --- 2. EXTRAÇÃO DA AMOSTRA (10k linhas) ---
query = """
    SELECT * FROM `gov-datalake-analytics.bronze.siape_bruto` 
    LIMIT 10000
"""
print("⏳ Baixando amostra de dados...")
df = client.query(query).to_dataframe()
print(f"✅ Dados carregados: {df.shape[0]} linhas e {df.shape[1]} colunas.")

# --- 3. AUDITORIA DE QUALIDADE (AQUI ENTRA O SEU CÓDIGO) ---
print("\n--- 🕵️ RELATÓRIO DE QUALIDADE (Manual) ---")

#Auditoria de ID (Unicidade)
total_linhas = len(df)
valores_unicos = df['Id_SERVIDOR_PORTAL'].nunique()
print(f'A base possui {total_linhas} linhas e os valores únicos da coluna Id são: {valores_unicos}')

#Auditoria de Completude
valores_nulos_cpf = df['CPF'].isnull().sum()
valores_nulos_orgaos = df['ORG_LOTACAO'].isnull().sum()
print(f'Os valores nulos da coluna CPF são: {valores_nulos_cpf} e da coluna ORG_LOTACAO são: {valores_nulos_orgaos}')

#Auditoria de Formato (Datas Estranhas)
print(f'O tipo de dado na coluna DATA_INGRESSO_CARGOFUNCAO é: {df['DATA_INGRESSO_CARGOFUNCAO'].dtype}')


