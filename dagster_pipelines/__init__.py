from dagster import Definitions
from dagster_pipelines.assets.bronze.siape import siape_ativos, siape_remuneracao, siape_aposentados, siape_afastamentos
from dagster_pipelines.assets.bronze.depro import depro_alocacao, depro_cargos, depro_aposentadorias
from dagster_pipelines.assets.bronze.enap import enap_capacitacao

defs = Definitions(
    assets = [depro_alocacao, depro_cargos, depro_aposentadorias,
              siape_ativos, siape_remuneracao, siape_aposentados, siape_afastamentos, enap_capacitacao]
)