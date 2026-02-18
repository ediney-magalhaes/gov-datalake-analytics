# 🏛️ Projeto Data Lake - Gestão de Pessoal (Governo Federal)

Projeto técnico de Arquitetura de Dados em Cloud para ingestão, tratamento e disponibilização de dados públicos do Governo Federal (folha de pagamento, aposentadorias e capacitação do executivo federal).

O objetivo é estruturar um Data Lake moderno em camadas (Bronze → Prata → Ouro), garantindo escalabilidade, governança, segurança e qualidade dos dados.

---

## 🎯 Contexto e Desafio de Negócio

O Poder Executivo Federal gera diariamente uma vasta quantidade de dados sobre a gestão de seus servidores. Historicamente, essas informações encontram-se dispersas em múltiplos sistemas heterogêneos (SIAPE, SouGov, SIAPEcad, etc.). 

**O Problema:** A extração manual ou semiautomatizada dessas bases fragmentadas compromete a agilidade, confiabilidade e interoperabilidade das informações, dificultando a visão estratégica e a tomada de decisão por parte do Ministério da Gestão e da Inovação (MGI).

**A Solução (Este Projeto):** Em alinhamento com a Estratégia Federal de Governo Digital (Portaria SGD/MGI nº 6.618/2024), este projeto constrói uma infraestrutura digital pública unificada. Através da **Arquitetura Medallion (Bronze, Silver, Gold)**, o pipeline automatiza a coleta, aplica regras de anonimização (LGPD) in-flight, e entrega bases consolidadas para subsidiar os Painéis Analíticos da Secretaria Extraordinária para a Transformação do Estado (SETE).

---

## 📊 Métricas Técnicas e Impacto (Resultados Alcançados)

A arquitetura *Cloud Native* desenvolvida com processamento em memória entregou os seguintes resultados de performance:

* **Volume de Dados Processado:** ~2.5 milhões de registros mensais (SIAPE + ENAP).
* **Tempo Médio de Ingestão:** ~5 minutos para carga total (Origem → Cloud).
* **Velocidade de Processamento (Throughput):** Picos de **+1.600 linhas processadas por segundo** (incluindo criptografia SHA-256 registro a registro).
* **Custo Estimado por Consulta (FinOps):** Redução de leitura de dados via partition pruning e cluster elimination no BigQuery (Consultas analíticas limitadas à casa dos Megabytes, mantendo o projeto dentro do *Free Tier* do GCP).
* **Taxa de Sucesso do Pipeline (Estimado):** Arquitetura projetada para alta disponibilidade, com meta de SLA técnico estimado em 99.9%.

---

## 📍 Status do Projeto

| Fase | Arquitetura | Status | Entregáveis |
| :--- | :--- | :---: | :--- |
| **Fase 1 (Local)** | Docker + PostgreSQL + Python | ✅ Concluída | Ingestão inicial + Diagnóstico de Qualidade |
| **Fase 2 (Cloud - Bronze)** | GCP BigQuery + Python | ✅ Concluída | Ingestão via API + Hash LGPD + Logs de Performance + UAT |
| **Fase 3 (Cloud - Prata/Ouro)** | BigQuery + dbt / SQL | 🚧 Em andamento | Limpeza, tipagem, modelagem dimensional (SCD) |

---

## 🧱 Arquitetura da Solução

**Fontes:** Portal da Transparência (SIAPE) e Escola Virtual Gov (ENAP)
⬇️
**Ingestão:** Python (Extração em Memória + Descompactação Complexa + Hash SHA-256)
⬇️
**Storage:** Google BigQuery (Camada Bronze)
⬇️
**Transformação:** dbt / SQL (Camadas Prata e Ouro)
⬇️
**Consumo:** Analytics & Dashboards de BI

---

## ⚙️ Principais Características Técnicas

🔹 **Estratégia de Modelagem Analítica e Data Warehousing (Fase 3)**
A arquitetura de consumo (Camada Ouro) foi desenhada sob o paradigma *Cloud Native*, optando por **Wide Table Analítica (OBT - One Big Table)** como estratégia otimizada para consumo analítico em BigQuery.

* **1. Granularidade Única e Clara:** 1 linha por servidor por mês de competência (Chave Primária Composta: `hash_cpf` + `mes_referencia`), evitando explosão de cardinalidade (fan-out).

* **2. Estrutura da OBT (Dimensões e Métricas):** * *Dimensões Congeladas:* Ministério de lotação, Cargo, UF, Tipo de Vínculo.
  * *Métricas Associadas:* Remuneração bruta/líquida, quantidade de cursos concluídos (ENAP), tempo de serviço.

* **3. Otimização Física (FinOps no BigQuery):** * `PARTITION BY` mês de competência (isolando fisicamente os custos de varredura).
  * `CLUSTER BY` órgão, UF e hash_cpf (acelerando os filtros nativos dos dashboards de BI).

* **4. Estratégia de Carga e Idempotência:** A OBT será materializada de forma **Incremental** (estratégia `insert_overwrite` gerenciada pelo dbt). Isso garante que reprocessamentos de um mesmo mês sobrescrevam cirurgicamente a partição, garantindo controle de custos, integridade dos dados e facilidade de *rollback*.

🔹 **Ingestão Cloud Native (Multi-Fontes)**
* Download automático de arquivos públicos massivos via APIs governamentais.
* Portal da Transparência (SIAPE): Extração via micro-batching de arquivos `.zip`.
* Escola Virtual Gov (ENAP): Extração e descompactação dupla (`.tar.gz` contendo `.gzip` interno) lidando com separadores não padronizados (`|`).
* Processamento direto em memória RAM (`io.BytesIO`), com eliminação de arquivos físicos locais (Zero disco).

🔹 **Conformidade com LGPD e Governança**
* Pseudonimização determinística de CPF via `SHA-256` *in-flight* (antes do armazenamento).
* Homologação técnica documentada simulando testes de aceitação do usuário (UAT).
* Versionamento rigoroso baseado no padrão *Conventional Commits*.

🔹 **Auditoria e Rastreabilidade**
* Logs estruturados e defensivos (`try/except`) registrando: Horário de execução, volumetria exata, falhas HTTP (ex: 404) e status transacional do BigQuery.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.12 LTS (Foco em estabilidade de dependências)
* **Bibliotecas Principais:** Pandas, google-cloud-bigquery, requests, hashlib, logging
* **Cloud Data Warehouse:** Google BigQuery
* **Transformação de Dados:** dbt Core (Data Build Tool)
* **Banco Local & Infra:** PostgreSQL 15 + Docker

---

## 📁 Estrutura do Repositório

```text
/
├── docs/                           # Documentação oficial (Arquitetura, Dicionário, UAT)
├── fase_1/                         # Scripts de ingestão inicial e diagnóstico local
├── fase_2/                         # Robôs Python de Ingestão Cloud Native (Bronze)
├── .gitignore                      # Proteção de credenciais GCP e logs locais
├── CONTRIBUTING.md                 # Políticas de versionamento (Conventional Commits)
└── README.md                       # Documentação principal
```
---

## 🎯 Objetivo Arquitetural

Construir uma base de dados pública estruturada, segura e escalável, preparada para Modelagem Analítica Avançada, Governança de Dados (FinOps) e criação de indicadores estratégicos para o Governo Federal

---

**Desenvolvido por Ediney Magalhães**  
Data & Analytics Engineering Project | Cloud Data Architecture
