# 🏛️ Projeto Data Lake - Gestão de Pessoal (Governo Federal)

Projeto técnico de Arquitetura de Dados em Cloud para ingestão, tratamento e disponibilização de dados públicos do Governo Federal (folha de pagamento, aposentadorias e diversidade do executivo federal).

O objetivo é estruturar um Data Lake moderno em camadas (Bronze → Prata → Ouro), garantindo escalabilidade, governança, segurança e qualidade dos dados.

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

🔹 **Ingestão Cloud Native (Multi-Fontes)**
* Download automático de arquivos públicos massivos via APIs governamentais.
* Portal da Transparência (SIAPE): Extração via micro-batching de arquivos `.zip`.
* Escola Virtual Gov (ENAP): Extração e descompactação dupla (`.tar.gz` contendo `.gzip` interno) lidando com separadores não padronizados (`|`).
* Processamento direto em memória RAM (`io.BytesIO`), com eliminação de arquivos físicos locais (Zero disco).

🔹 **Micro-Batching, Performance e Gestão de Memória**
* Processamento de arquivos com +2.3 milhões de linhas mensais.
* Monitoramento de performance com cálculo matemático em tempo real (Registrando picos de **+1.600 linhas processadas por segundo**).
* Liberação imediata de memória após carga, prevenindo erros de *Out Of Memory (OOM)*.

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
