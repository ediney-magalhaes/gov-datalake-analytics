# gov-datalake-analytics — dbt Core

Projeto dbt responsável pela Camada Silver (e, futuramente, Gold) do Data Lake de Gestão de Pessoal do Governo Federal (PNUD BRA/21/011 — MGI/SETE/SGP).

## Convenção de nomes

Modelos de staging seguem o padrão `stg_<fonte>__<entidade>` (dois underscores entre fonte e entidade), por exemplo:

- `stg_siape__ativos`
- `stg_depro__alocacao`
- `stg_enap__capacitacao`

## Estrutura
```
models/
└── staging/
├── siape/ # siape_sources.yml + 4 modelos (ativos, remuneração, aposentados, afastamentos)
├── depro/ # depro_sources.yml + 3 modelos (alocação, cargos, aposentadorias)
└── enap/ # enap_sources.yml + 1 modelo (capacitação)
macros/
└── converte_valor_brl.sql # conversão de valores monetários BR (vírgula decimal) para FLOAT64

```

## Fontes (sources)

Cada fonte tem seu próprio arquivo `<fonte>_sources.yml`, apontando para External Tables no dataset `bronze` do BigQuery (Parquet particionado por `year`/`month` no GCS).

## Rodando o projeto

```powershell
# Compilar um modelo específico (sem materializar)
dbt compile --select stg_siape__ativos

# Materializar um modelo específico
dbt run --select stg_siape__ativos

# Materializar todos os modelos de staging
dbt run --select staging
```

## Decisões relevantes

- **ADR-009** (`docs/adrs/`): estratégia de chave universal de cruzamento (`id_servidor_portal`). ENAP não participa do linkage — ver correção de 02/08/2026.
- Datas são convertidas com `SAFE.PARSE_DATE`/`SAFE.PARSE_DATETIME` (nunca a versão sem `SAFE.`, para não quebrar a query em valores inválidos).
- Colunas monetárias em formato brasileiro (`R$ 1.234,56`) usam o macro `converte_valor_brl`.
- `nome` é excluído de todos os modelos de staging por convenção de governança/LGPD.

## Recursos gerais do dbt

- [Documentação oficial](https://docs.getdbt.com/docs/introduction)
- [Discourse](https://discourse.getdbt.com/) — perguntas frequentes
- [Slack da comunidade](https://community.getdbt.com/)
