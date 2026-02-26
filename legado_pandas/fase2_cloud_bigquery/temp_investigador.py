import io
import requests
import zipfile

periodo = '202501'
url = f'https://portaldatransparencia.gov.br/download-de-dados/servidores/{periodo}_Servidores_SIAPE'

resposta = requests.get(url, verify=False)

arquivo_zip = io.BytesIO(resposta.content)

for lista in zipfile.ZipFile(arquivo_zip).namelist():
    print(lista)
