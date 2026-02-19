# 🏛️ Projeto Data Lake - Gestão de Pessoal (Governo Federal)

Projeto técnico de Arquitetura de Dados em Cloud para ingestão, tratamento e disponibilização de dados públicos do Governo Federal (folha de pagamento, aposentadorias e capacitação do executivo federal).

O objetivo é estruturar um **Data Lake moderno em camadas (Bronze → Prata → Ouro)**, garantindo escalabilidade, governança, segurança e qualidade dos dados.

---

## 🎯 Contexto e Desafio de Negócio

O Poder Executivo Federal gera diariamente uma vasta quantidade de dados sobre a gestão de seus servidores. Historicamente, essas informações encontram-se dispersas em múltiplos sistemas heterogêneos (SIAPE, SouGov, SIAPEcad, etc.).

### O Problema
A extração manual ou semiautomatizada dessas bases fragmentadas compromete a agilidade, confiabilidade e interoperabilidade das informações, dificultando a visão estratégica e a tomada de decisão por parte do Ministério da Gestão e da Inovação (MGI).

### A Solução (Este Projeto)
Em alinhamento com a Estratégia Federal de Governo Digital (Portaria SGD/MGI nº 6.618/2024), este projeto constrói uma infraestrutura digital pública unificada.  
Através da **Arquitetura Medallion (Bronze, Silver, Gold)**, o pipeline:

- Automatiza a coleta
- Aplica anonimização (LGPD) in-flight
- Entrega bases consolidadas para subsidiar painéis estratégicos

---

## 📊 Métricas Técnicas e Impacto (Resultados Alcançados)

A arquitetura *Cloud Native* desenvolvida com processamento em memória entregou resultados expressivos de performance e resiliência, comprovados em testes de *stress*:

- **Volume Processado:** ~5.9 milhões de registros (SIAPE Ativos + SIAPE Aposentados + ENAP)
- **Tempo Médio de Ingestão:** ~5.3 minutos (Origem → BigQuery)
- **Throughput:** 15.501 linhas/segundo (incluindo descompactação + SHA-256 registro a registro)

> 📐 **Nota técnica:** O throughput foi calculado via logging estruturado, dividindo o volume total de registros pelo tempo total de execução do loop de ingestão.

- **Consumo de Disco Local:** 0 bytes (Processamento 100% `in-memory` via `io.BytesIO`)
- **Otimização de Custos (FinOps):** Uso de *partition pruning* e *cluster elimination*, mantendo consultas na casa dos MBs (Free Tier GCP)
- **Taxa de Sucesso Observada:** 100% nas execuções de stress test realizadas até o momento (sem ocorrência de timeouts após mitigação via headers customizados e micro-batching)

---

## ✅ Qualidade de Dados (Fase 3)

A confiabilidade da Camada Prata é garantida por testes automatizados via **dbt Core**:

- **Auditoria de Unicidade:** Implementação de teste de chave composta (`hash_cpf` + `mes_competencia` + `id_vinculo`) para evitar duplicidade de pagamentos.
- **Tratamento de Duplicidade Técnica:** Deduplicação via `ROW_NUMBER()` para neutralizar falhas de envio da fonte de dados (Portal da Transparência).
- **Integridade de Campos:** 100% de conformidade nos testes de `not_null` para identificadores e nomes.

---

## 📍 Status do Projeto

| Fase | Arquitetura | Status | Entregáveis |
|------|------------|--------|------------|
| Fase 1 (Local) | Docker + PostgreSQL + Python | ✅ Concluída | Ingestão inicial + Diagnóstico |
| Fase 2 (Cloud - Bronze) | BigQuery + Python | ✅ Concluída | Ingestão via API + Hash LGPD + Logs |
| Fase 3 (Cloud - Prata/Ouro) | BigQuery + dbt | 🚧 Em andamento | Camada de Staging + Testes de Qualidade |

---

## 🧱 Arquitetura da Solução

**Fontes:**  
Portal da Transparência (SIAPE)  
Escola Virtual Gov (ENAP)

⬇️  
**Ingestão:** Python (Extração em memória + Descompactação + SHA-256)  
⬇️  
**Storage:** Google BigQuery (Bronze)  
⬇️  
**Transformação:** dbt / SQL (Prata e Ouro)  
⬇️  
**Consumo:** Dashboards e Analytics

---

## ⚙️ Principais Características Técnicas

### 🔹 Modelagem Analítica (Fase 3)

A camada de consumo (Ouro) adota uma estratégia **Cloud Native**, optando por:

### ✅ Wide Table Analítica (OBT - One Big Table)

#### 1️⃣ Granularidade
- 1 linha por servidor por mês
- Chave composta: `hash_cpf + mes_referencia`
- Evita explosão de cardinalidade (fan-out)

#### 2️⃣ Estrutura
**Dimensões congeladas:**
- Ministério
- Cargo
- UF
- Tipo de vínculo

**Métricas:**
- Remuneração bruta e líquida
- Quantidade de cursos ENAP
- Tempo de serviço

#### 3️⃣ Otimização Física (FinOps)
- `PARTITION BY mes_referencia`
- `CLUSTER BY orgao, uf, hash_cpf`

#### 4️⃣ Estratégia Incremental
Materialização via `insert_overwrite` (dbt), garantindo:

- Idempotência
- Controle de custos
- Facilidade de rollback

---

### 🔹 Ingestão Cloud Native

- Download automatizado via APIs públicas
- Micro-batching de arquivos `.zip`
- Descompactação dupla (`.tar.gz` + `.gzip`)
- Processamento 100% em memória (`io.BytesIO`)
- Zero persistência local

---

### 🔹 Conformidade LGPD

- Pseudonimização determinística (`SHA-256`) aplicada antes do armazenamento
- Nenhum dado sensível salvo em texto claro
- Versionamento via Conventional Commits

---

### 🔹 Auditoria

- Logs estruturados
- Captura de erros HTTP (404, 500)
- Registro de volumetria e tempo de execução

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.12 LTS**
- Pandas
- google-cloud-bigquery
- requests
- hashlib
- logging
- dbt Core
- PostgreSQL + Docker

---

## ▶️ Como Executar (Camada Bronze)

### 1 Pré-requisitos

- Python 3.12+
- Conta GCP ativa
- Dataset criado no BigQuery
- Service Account com:
  - BigQuery Data Editor
  - BigQuery User

### 2 Configuração

```bash
export GOOGLE_APPLICATION_CREDENTIALS="caminho/para/sua-chave.json"
```
### 3 Execução
```bash
python fase_2/00_orquestrador_bronze.py
```
### 4 Resultado Esperado
- Tabelas criadas/atualizadas no BigQuery
- Logs de execução estruturados

---

## 📁 Estrutura do Repositório
```
/
├── docs/                 # Documentação, Dicionários e Homologações
├── fase_1/               # Scripts iniciais locais
├── fase_2/               # Ingestão Cloud (Python)
├── analytics_gov/        # Projeto dbt (Camada Prata e Transformação)
├── .gitignore
├── CONTRIBUTING.md
└── README.md
```
---

## 🚀 Roadmap Técnico – Fase 3

### Camada Prata
- Tipagem estrita (DATE, NUMERIC) 
- Tratamento de nulos
- dbt tests (`not_null`, `unique`, `accepted_values`)
- SCD Tipo 2

### Camada Ouro
- Materialização incremental (insert_overwrite)
- PARTITION BY mes_referencia
- CLUSTER BY orgao, uf, hash_cpf

### Governança
- Data lineage via `dbt docs`
- Controle de mudanças via Git

---

## 🎯 Objetivo Final
Construir uma base pública estruturada, segura e escalável, pronta para modelagem analítica avançada e indicadores estratégicos.

---
**Ediney Magalhães**
Data & Analytics Engineering Project
Cloud Data Architecture