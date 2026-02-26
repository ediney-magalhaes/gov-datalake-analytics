import io
import requests
import zipfile
import polars as pl

#definindo caminho para acessar os dados
periodo = '202501'
url = f'https://portaldatransparencia.gov.br/download-de-dados/servidores/{periodo}_Servidores_SIAPE'

#obtendo retorno da url em bytes
resposta = requests.get(url, verify=False)
arquivo_zip = io.BytesIO(resposta.content)

#abrindo o arquivo zip
with zipfile.ZipFile(arquivo_zip) as z:
    nome_csv = f'{periodo}_Cadastro.csv'

    #extraindo o arquivo
    arquivo_extraido = z.open(nome_csv)

    #lendo o arquivo com o Polars
    df_cadastro = pl.read_csv(arquivo_extraido.read(), separator=';', encoding='latin1')

print(df_cadastro.head())