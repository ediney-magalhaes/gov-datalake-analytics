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

print("--- INICIANDO DIAGNÓSTICO PROFUNDO (AUDITORIA TOTAL) ---")

##df = pd.read_sql('cadastro_bronze', engine)
query = 'SELECT * FROM cadastro_bronze'
df = pd.read_sql(query, engine)
auditoria = []
for coluna in df.columns:
    print(f'Analisando: {coluna}')

    #Cálculos
    qtd_nulos = df[coluna].isnull().sum()
    qtd_unicos = df[coluna].nunique()
    top_valores = df[coluna].value_counts().head(5).to_dict()

    #Guardar
    auditoria.append({
        'Coluna': coluna,
        'Nulos': qtd_nulos,
        'Unicos': qtd_unicos,
        'Exemplos': top_valores
    })
#Salvar
print("Gerando relatório CSV...")
df_auditoria = pd.DataFrame(auditoria)
df_auditoria.to_csv('dicionario_dados_auditado.csv', index=False, sep=';')
print("Sucesso! Arquivo 'dicionario_dados_auditado.csv' gerado")