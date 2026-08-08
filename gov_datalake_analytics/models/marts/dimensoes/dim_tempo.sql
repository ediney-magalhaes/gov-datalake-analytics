with todos_periodos as(
    select distinct year, month
    from {{ ref('stg_siape__afastamentos') }}
    union distinct
    select distinct year, month
    from {{ ref('stg_siape__aposentados') }}
    union distinct
    select distinct year, month
    from {{ ref('stg_siape__ativos') }}
    union distinct
    select distinct year, month
    from {{ ref('stg_siape__remuneracao') }}
    union distinct
    select distinct year, month
    from {{ ref('stg_depro__alocacao') }}
    union distinct
    select distinct year, month
    from {{ ref('stg_depro__aposentadorias') }}
    union distinct
    select distinct year, month
    from {{ ref('stg_depro__cargos') }}
    union distinct
    select distinct year, month
    from {{ ref('stg_enap__capacitacao') }}
)
select
    year,
    month,
    case
        when month in (1,2,3) then 1
        when month in (4,5,6) then 2
        when month in (7,8,9) then 3
        when month in (10,11,12) then 4
    end as trimestre,
    case
        when month = 1 then 'Janeiro'
        when month = 2 then 'Fevereiro'
        when month = 3 then 'Março'
        when month = 4 then 'Abril'
        when month = 5 then 'Maio'
        when month = 6 then 'Junho'
        when month = 7 then 'Julho'
        when month = 8 then 'Agosto'
        when month = 9 then 'Setembro'
        when month = 10 then 'Outubro'
        when month = 11 then 'Novembro'
        when month = 12 then 'Dezembro'
    end as nome_mes,
    concat(cast(year as string), '-', lpad(cast(month as string), 2, '0')) as ano_mes
from todos_periodos