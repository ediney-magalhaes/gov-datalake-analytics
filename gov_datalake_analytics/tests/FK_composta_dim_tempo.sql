select
    f.year,
    f.month
from {{ ref('fct_remuneracao') }} f
left join {{ ref('dim_tempo') }} t
on f.year = t.year and f.month = t.month
where t.year is null