import pandas as pd
arquivo = 'cadastro_siape_bruto.csv'
df_cadastro = pd.read_csv(arquivo, sep=';', encoding='iso-8859-1', nrows=100)
print(df_cadastro.columns)
print(df_cadastro.dtypes)

print('\n---GERADOR SQL AUTOMÁTICO---')
print('CREATE TABLE cadastro_bronze (')
for coluna, tipo in df_cadastro.dtypes.items():
    tipo_sql = 'VARCHAR(255)'
    if 'int' in str(tipo):
        tipo_sql = 'BIGINT'

    print(f' {coluna} {tipo_sql},')
print(');')