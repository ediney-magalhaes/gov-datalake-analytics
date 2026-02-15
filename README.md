# 🏛️ Projeto Data Lake - Gestão de Pessoal (Governo Federal)

Repositório oficial para os artefatos técnicos (Simulação Prática).
Este projeto visa estruturar a arquitetura de dados para análise de folha de pagamento, aposentadorias e diversidade do executivo federal.

---

📍 Status do Projeto

| Fase | Arquitetura | Status | Entregáveis |
|---|---|---|---|
| Fase 1 (Local) | Docker + Postgres + Python | ✅ Concluída | Ingestão Bronze e Diagnóstico Inicial |
| Fase 2 (Nuvem - Bronze) | GCP BigQuery + Python Automático | ✅ Concluída (Produto 2) | Ingestão Automática via API, Criptografia LGPD (SHA-256) e Logs de Auditoria |
| Fase 3 (Nuvem - Prata/Ouro) | GCP BigQuery + dbt/SQL | 🚧 Em Andamento | Limpeza de Nulos, Tipagem e Painéis Analíticos |
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
* **Cloud Data Warehouse:** Google BigQuery
* **Segurança e Conformidade:** `hashlib` (Mascaramento de CPF / LGPD)
* **Ingestão Automática:** `requests`, `io`, `zipfile`

## ⚙️ Arquitetura da Solução: Camada Bronze (Fase 2)

A fase de ingestão para a nuvem (GCP) foi construída focando em **automação, resiliência e segurança**, cumprindo os requisitos do edital para o Produto 2.

* **Automação de Ingestão (Cloud Native):** O pipeline em Python acessa as URLs públicas do governo (API/Portal da Transparência), faz o download dos arquivos `.zip`, descompacta na memória RAM (`io.BytesIO`) e lê os dados diretamente, eliminando a necessidade de arquivos físicos locais e trabalho manual.
* **Micro-Batching e Gestão de Memória:** Como os arquivos contêm mais de 2.3 milhões de linhas mensais, o pipeline foi desenhado em uma arquitetura de lote iterativo (*micro-batching*). O script extrai, trata, carrega no BigQuery (`google-cloud-bigquery`) e deleta o dado da memória RAM imediatamente, prevenindo erros de *Out of Memory* (OOM).
* **Conformidade com LGPD (Pseudonimização):** Em estrito cumprimento à Lei Geral de Proteção de Dados, a coluna `CPF` sofre um processo de *Hashing* determinístico (SHA-256) no momento da extração, antes de tocar o banco de dados. Isso garante a proteção do dado pessoal sensível ao mesmo tempo que permite cruzamentos futuros (Joins) com outras bases.
* **Auditoria Contínua:** Todo o processo gera logs de rastreabilidade (biblioteca `logging`), registrando horários de início, falhas de conexão (ex: Erros 404), volumetria processada e status de entrega no GCP.

---
*Desenvolvido por Ediney Magalhães - Analytics Engineer*
