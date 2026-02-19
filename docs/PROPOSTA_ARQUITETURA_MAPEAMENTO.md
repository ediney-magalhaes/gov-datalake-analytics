# 🏗️ Proposta de Arquitetura de Pipelines de Dados (Produto 1)

**Projeto:** Data Lake - Gestão de Pessoal (Governo Federal)  
**Objetivo:** Definição da arquitetura técnica do fluxo de dados (Ingestão → Transformação → Consumo), governança, modelagem e mitigação de riscos operacionais.

---

# 1️⃣ Visão Geral da Arquitetura

A solução adota o paradigma **Medallion Architecture (Bronze → Prata → Ouro)**, implementado integralmente em ambiente *Cloud Native* (Google Cloud Platform), priorizando:

- Escalabilidade elástica
- Processamento colunar otimizado
- Conformidade LGPD
- Controle de custos (FinOps)
- Governança orientada a dados

---

## 🥉 Camada Bronze — Ingestão Bruta

Responsável pela captura fiel dos dados da origem, preservando rastreabilidade histórica.

### Características Técnicas:

- Extração via APIs públicas governamentais
- Processamento 100% em memória (`io.BytesIO`)
- Descompactação dupla (`.zip` e `.tar.gz`)
- Micro-batching mensal
- Persistência em Google BigQuery

### Segurança (LGPD):

- Pseudonimização determinística (`SHA-256`) aplicada **in-flight**
- Nenhum arquivo bruto salvo localmente
- Criptografia antes da persistência em nuvem

### Estratégia de Carga:

- `WRITE_APPEND`
- Controle incremental por mês de competência
- Logs estruturados registrando volumetria, tempo e status HTTP

---

## 🥈 Camada Prata — Transformação e Qualidade (dbt)

Responsável pela limpeza técnica, padronização e integridade histórica.

### Regras Implementadas:

- Tipagem estrita (`DATE`, `NUMERIC`, `STRING`)
- Padronização snake_case
- Remoção de sujeira técnica
- Deduplicação por vínculo funcional via:

```sql
ROW_NUMBER() OVER (PARTITION BY hash_cpf, id_vinculo, mes_competencia)
```

### Garantia de Unicidade:

Chave composta:

```sql
hash_cpf + mes_competencia + id_vinculo
```

Validada por:

- `dbt test`
- `unique`
- `not_null`
- `accepted_values`

---

## 🥇 Camada Ouro — Consumo Analítico

Modelo otimizado para consumo em bancos colunares (BigQuery).

### Estratégia Adotada:

- ✅ OBT (One Big Table)
- ❌ Evita Star Schema clássico (custoso em JOINs)

### Granularidade Final:

**1 linha por vínculo funcional por mês de competência**

Essa decisão preserva:
- Acumuladores de cargo
- Múltiplos vínculos
- Integridade financeira histórica

---

## 🔧 Otimização Física (FinOps)

A modelagem da Camada Ouro foi desenhada para explorar ao máximo o mecanismo colunar do BigQuery.

### Estratégias Implementadas

- `PARTITION BY mes_referencia`
- `CLUSTER BY orgao, uf, hash_cpf`
- Materialização incremental via `insert_overwrite` (dbt)
- Reprocessamento cirúrgico por partição (idempotência garantida)

### Benefícios Técnicos

- Redução significativa de leitura colunar (partition pruning)
- Aceleração de filtros analíticos (cluster elimination)
- Previsibilidade orçamentária
- Facilidade de rollback por mês
- Evita reprocessamento histórico completo

---

# 2️⃣ Fluxo Operacional do Pipeline

1. **Orquestração:** `00_orquestrador_bronze.py`
2. **Extract:** Requisição HTTP com headers customizados
3. **Load (RAM):** Descompactação e parsing em memória (`io.BytesIO`)
4. **Security Transform:** Aplicação de hash `SHA-256`
5. **Load (Cloud):** Ingestão incremental no BigQuery
6. **Transform (dbt):** Modelagem e testes automatizados
7. **Exposição:** Consumo por ferramentas de BI e Analytics

---

# 3️⃣ Matriz de Riscos Técnicos e Mitigações

| Risco Técnico | Impacto | Mitigação Implementada |
|---------------|----------|-------------------------|
| Bloqueio ou instabilidade de API governamental | Alto | `try/except`, timeout configurado (120s), User-Agent customizado |
| Estouro de Memória (OOM) | Alto | Processamento iterativo mensal + `del df_mes` |
| Vazamento de PII | Gravíssimo | Hash `SHA-256` aplicado antes da persistência |
| Duplicidade na origem | Médio | Deduplicação via `ROW_NUMBER()` + testes de chave composta no dbt |
| Crescimento volumétrico | Médio | Arquitetura incremental + particionamento físico |
| Custo excessivo em nuvem | Médio | Partition pruning + cluster elimination |

---

# 4️⃣ Governança e Modelagem

## 📌 Data Lineage

Gerenciado automaticamente via `dbt docs`, garantindo rastreabilidade completa:

```
Source → Bronze → Prata → Ouro
```

## 📌 Política de Retenção

- Bronze: histórico bruto controlado
- Prata: dados confiáveis e tratados
- Ouro: camada analítica otimizada para consumo

## 📌 Analytics as Code

- Transformações versionadas em Git
- Controle via Conventional Commits
- Testes automatizados com `dbt test`
- Reprocessamento incremental idempotente

---

# 🎯 Princípios Arquiteturais

- Segurança antes da persistência
- Transformação após armazenamento (ELT)
- Processamento incremental
- Idempotência garantida
- Governança orientada a testes
- Otimização para banco colunar
