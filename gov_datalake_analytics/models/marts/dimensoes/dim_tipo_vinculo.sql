select 
    cod_tipo_vinculo,
    tipo_vinculo
from {{ ref('stg_siape__ativos') }}
union distinct
select
    cod_tipo_vinculo,
    tipo_vinculo
from {{ ref('stg_siape__aposentados') }}