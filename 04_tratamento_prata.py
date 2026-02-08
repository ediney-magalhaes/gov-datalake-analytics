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

query = 'SELECT * FROM cadastro_bronze;'
df = pd.read_sql(query, engine)
print(f'Total antes: {len(df)}')

mapa_romanos = {'I':1, 'II':2, 'III':3, 'IV':4, 'V':5, 'VI':6}
df['padrao_cargo'] = df['padrao_cargo'].replace(mapa_romanos)
df['padrao_cargo_ajustada'] = pd.to_numeric(df['padrao_cargo'], errors='coerce')
df = df.dropna(subset=['cpf'])

# Lista do que consideramos "Trabalhadores Ativos"
tipos_validos = [
    'ATIVO PERMANENTE',
    'CONTRATO TEMPORARIO',
    'NOMEADO CARGO COMIS.',
    'CEDIDO/REQUISITADO',
    'RESIDENCIA E PMM'
]

print(f'Filtrando apenas vinculos ativos relevantes...')
df = df[df['situacao_vinculo'].isin(tipos_validos)]
print(f'Total após o filtro de vínculos: {len(df)}')

df.to_sql('servidores_prata', engine, if_exists='replace', index=False)
print(f'Total depois: {len(df)}')