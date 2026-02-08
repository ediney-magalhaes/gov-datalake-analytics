import pandas as pd
from sqlalchemy import create_engine
import os

# Configurações
ARQUIVO_ENTRADA = '/data/dados.csv'

# String de Conexão: tipo://usuario:senha@onde_esta_o_banco:porta/nome_banco
# Note que 'db_hospital' é o nome do serviço que demos no docker-compose!
DB_CONNECTION = 'postgresql://admin:segredo@db_hospital:5432/conahp_db'

print("--- INICIANDO ETL COM BANCO DE DADOS ---")

try:
    # 1. Extract (Ler CSV)
    print(f"Lendo arquivo: {ARQUIVO_ENTRADA}...")
    df = pd.read_csv(ARQUIVO_ENTRADA)

    # 2. Transform (Simples limpeza para garantir)
    # Vamos garantir que as colunas do CSV batam com o banco
    # Supondo que seu CSV já tenha colunas compatíveis. 
    # Se não tiver, o Pandas tenta adaptar.
    
    print("Processando dados...")
    # Exemplo: Renomeando colunas se necessário (ajuste conforme seu CSV real se der erro)
    # df = df.rename(columns={'Customer': 'hospital', ...})

    # 3. Load (Inserir no Postgres)
    print("Conectando ao Banco de Dados...")
    engine = create_engine(DB_CONNECTION)
    
    print("Inserindo dados na tabela 'internacoes'...")
    # if_exists='append': Adiciona os dados sem apagar os antigos
    # index=False: Não envia o número da linha do Excel/CSV
    df.to_sql('internacoes', engine, if_exists='append', index=False)
    
    print("--- SUCESSO! DADOS SALVOS NO POSTGRESQL ---")

except Exception as e:
    print(f"❌ ERRO CRÍTICO: {e}")