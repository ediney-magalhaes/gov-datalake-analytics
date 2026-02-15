import pandas as pd
from sqlalchemy import create_engine

usuario = 'admin'
password = 'segredo'
host = 'localhost'
port = '5432'
db_name = 'db_governo_mgi'
url_conexao = f'postgresql+psycopg2://{usuario}:{password}@{host}:{port}/{db_name}'
engine = create_engine(url_conexao)
print(engine)

arquivo = '202511_Cadastro.csv'

df_cadastro_bronze = pd.read_csv(arquivo, sep=';', encoding='iso-8859-1')
df_cadastro_bronze.columns = df_cadastro_bronze.columns.str.lower()
df_cadastro_bronze.to_sql('aposentados_bronze', engine, if_exists='replace', index=False)