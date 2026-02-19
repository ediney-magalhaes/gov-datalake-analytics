# 📊 Analytics Gov — Camada Prata (dbt)

Este diretório contém o projeto **dbt Core** responsável pelas transformações da **Camada Prata (Staging + Normalização)** do Data Lake do Governo Federal.

A camada Prata tem como objetivo:

- Padronizar e tipar dados da Camada Bronze
- Garantir integridade e unicidade
- Aplicar regras técnicas de deduplicação
- Preparar a base para modelagem analítica (Camada Ouro)

---

## 🚀 Como Executar o Projeto

### 1️⃣ Instalar Dependências

Na primeira execução, instalar os pacotes necessários:

```bash
dbt deps
```

### 2️⃣ Executar Transformações

Criar as tabelas e views no BigQuery:

```bash
dbt run
```

### 3️⃣ Executar Testes de Qualidade

Validar integridade, unicidade e conformidade dos dados:

```bash
dbt test
```

---

## 🛠️ Regras de Engenharia Implementadas

🔹 Deduplicação Inteligente

Uso de `ROW_NUMBER()` com partição por:

- `hash_cpf`
- `mes_competencia`
- `id_vinculo`

Garantindo unicidade mesmo em caso de reenvio duplicado da fonte governamental.

---

🔹 Padronização Técnica

- Conversão de colunas para snake_case
- Tipagem explícita (CAST para DATE, NUMERIC, STRING)
- Limpeza de strings com TRIM()
- Normalização de campos categóricos

---

🔹 Qualidade de Dados (Produto 3)

Implementação de testes automatizados via dbt:

- `not_null`
- `unique`
- `accepted_values`
- Teste de chave composta (`hash_cpf + mes_competencia + id_vinculo`)

---

## 📁 Estrutura do Projeto
```
models/
└── staging/
    ├── stg_siape.sql
    ├── stg_enap.sql
    └── _stg_siape__models.yml
```
- `staging/`: Transformações e limpeza da Camada Prata
- `*.yml`: Documentação de colunas e definição de testes

---

## 📈 Próximos Passos (Camada Ouro)

- Construção da OBT (One Big Table)
- Materialização incremental (`insert_overwrite`)
- Particionamento por `mes_referencia`
- Clusterização por `orgao`, `uf`, `hash_cpf`
- Geração de Data Lineage via `dbt docs`