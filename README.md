# 🏛️ Projeto Data Lake - Gestão de Pessoal (Governo Federal)

Repositório oficial para os artefatos técnicos (Simulação Prática).
Este projeto visa estruturar a arquitetura de dados para análise de folha de pagamento, aposentadorias e diversidade do executivo federal.

---

## 📍 Status do Projeto
| Fase | Arquitetura | Status | Entregáveis |
| :--- | :--- | :--- | :--- |
| **Fase 1 (Local)** | Docker + Postgres + Python | ✅ Concluída | Ingestão Bronze e Diagnóstico Inicial |
| **Fase 2 (Nuvem)** | Google BigQuery + dbt | 🚧 A Iniciar | Tratamento Prata e Analytics Ouro |

---

## 📂 Estrutura do Repositório

* **[`RELATORIO_DIAGNOSTICO.md`](./RELATORIO_DIAGNOSTICO.md)**: 📄 Relatório técnico detalhado com o diagnóstico da qualidade dos dados (SIAPE/Aposentados), volumetria e matriz de riscos.
* **Scripts de Ingestão (`.py`)**: Códigos Python utilizados para extração e carga inicial no Data Lake local.
* **Docker Compose**: Definição da infraestrutura de banco de dados (PostgreSQL) utilizada na Fase 1.

---

## 🛠️ Tecnologias Utilizadas (Fase 1)
* **Linguagem:** Python 3.13 (Pandas, SQLAlchemy)
* **Banco de Dados:** PostgreSQL 15
* **Containerização:** Docker
* **Auditoria:** SQL Analítico e SQL para Auditoria de Dados

---
*Desenvolvido por Ediney Magalhães - Analytics Engineer*