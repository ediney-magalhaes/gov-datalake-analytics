import os
from dotenv import load_dotenv
from pipeline_bronze_raw_api import ingestao_bronze_raw_api
from pipeline_bronze_raw_polars import ingestao_bronze_raw_zip
from pipeline_bronze_normalized import normalizacao_da_bronze_raw

#carregar variáveis de ambiente
load_dotenv()

#configurando parâmetros SIGEPE
#bases_api = [{'sistema': 'sigepe', 'ano': '2025', 'mes': '01',
#              'url_api': 'https://apigateway.conectagov.estaleiro.serpro.gov.br/api-consulta-siape/v1/consulta-siape',
#              'chave_autorizacao': os.getenv('CHAVE_SIGEPE')}]

#configurando parâmetros PEsquisa de vozes
#bases_arquivos = [{'sistema': 'pesquisa_vozes', 'ano': '2024', 'mes': '01',
#                   'url_download': 'https://www.gov.br/gestao/pt-br/assuntos/pesquisa-vozes/arquivos/microdados_vozes_1_edicao.zip',
#                    'nome_arquivo_interno': 'microdados_vozes.csv'}]

#for base in bases_arquivos:
#    ingestao_bronze_raw_zip(sistema=base['sistema'], ano=base['ano'], mes=base['mes'], url_download=base['url_download'], nome_arquivo_interno=base['nome_arquivo_interno'])

#configurando parâmetros base DEPRO
bases_arquivos = [
#    {'sistema': 'depro_alocacao', 'ano': '2025', 'mes': '07', 'url_download': 'https://repositorio.dados.gov.br/seges/raio-x/raiox-2025-07.zip','nome_arquivo_interno':'alocacao-servidores.csv'},
    {'sistema':'depro_cargos','ano': '2025', 'mes': '07', 'url_download': 'https://repositorio.dados.gov.br/seges/raio-x/raiox-2025-07.zip', 'nome_arquivo_interno':'cargos-efetivos.csv'},
    {'sistema':'depro_aposentadorias','ano': '2025', 'mes': '07', 'url_download': 'https://repositorio.dados.gov.br/seges/raio-x/raiox-2025-07.zip','nome_arquivo_interno':'projecao-aposentadorias.csv' }]

for base in bases_arquivos:
    ingestao_bronze_raw_zip(sistema=base['sistema'], ano=base['ano'], mes=base['mes'],
                            url_download=base['url_download'], nome_arquivo_interno=base['nome_arquivo_interno'])
    normalizacao_da_bronze_raw(sistema= base['sistema'], ano= base['ano'], mes=base['mes'])

#configurando parâmetros base SIAPE
#bases_arquivos = [
#    {'sistema': 'siape_ativos', 'ano': '2025', 'mes': '01', 'url_download': 'https://portaldatransparencia.gov.br/download-de-dados/servidores/202501_Servidores_SIAPE','nome_arquivo_interno':'202501_Cadastro.csv'},
#    {'sistema':'siape_remuneracao','ano': '2025', 'mes': '01', 'url_download': 'https://portaldatransparencia.gov.br/download-de-dados/servidores/202501_Servidores_SIAPE', 'nome_arquivo_interno':'202501_Remuneracao.csv'},
#    {'sistema':'siape_aposentados','ano': '2025', 'mes': '01', 'url_download': 'https://portaldatransparencia.gov.br/download-de-dados/servidores/202501_Aposentados_SIAPE', 'nome_arquivo_interno':'202501_Cadastro.csv'},
#    {'sistema':'siape_afastamentos','ano': '2025', 'mes': '01', 'url_download': 'https://portaldatransparencia.gov.br/download-de-dados/servidores/202501_Servidores_SIAPE', 'nome_arquivo_interno':'202501_Afastamentos.csv'}]

#for base in bases_arquivos:
#    ingestao_bronze_raw_zip(sistema=base['sistema'], ano=base['ano'], mes=base['mes'],
#                            url_download=base['url_download'], nome_arquivo_interno=base['nome_arquivo_interno'])
#    normalizacao_da_bronze_raw(sistema= base['sistema'], ano= base['ano'], mes=base['mes'])
