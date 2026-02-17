# 🏛️ Projeto Data Lake - Gestão de Pessoal (Governo Federal)

Projeto técnico de Arquitetura de Dados em Cloud para ingestão, tratamento e disponibilização de dados públicos do Governo Federal (folha de pagamento, aposentadorias e diversidade do executivo federal).

O objetivo é estruturar um Data Lake moderno em camadas (Bronze → Prata → Ouro), garantindo escalabilidade, governança, segurança e qualidade dos dados.

---

## 📍 Status do Projeto

| Fase | Arquitetura | Status | Entregáveis |
|------|------------|--------|-------------|
| Fase 1 (Local) | Docker + PostgreSQL + Python | ✅ Concluída | Ingestão inicial + Diagnóstico de Qualidade |
| Fase 2 (Cloud - Bronze) | GCP BigQuery + Python (Cloud Native) | ✅ Concluída | Ingestão automática via API + Hash LGPD + Logs |
| Fase 3 (Cloud - Prata/Ouro) | BigQuery + dbt/SQL | 🚧 Em andamento | Limpeza, tipagem, modelagem analítica |

---

## 🧱 Arquitetura da Solução

Fontes: Portal da Transparência (SIAPE) e Escola Virtual Gov (ENAP)  
↓  
Python (Extração em Memória + Descompactação Complexa + Hash SHA-256)  
↓  
Google BigQuery (Camada Bronze)  
↓  
dbt / SQL (Camadas Prata e Ouro)  
↓  
Consumo Analítico (BI / Dashboards)

---

## ⚙️ Principais Características Técnicas

### 🔹 Ingestão Cloud Native (Multi-Fontes)

- Download automático de arquivos públicos massivos via APIs governamentais.
- **Portal da Transparência (SIAPE):** Extração via micro-batching de arquivos `.zip`.
- **Escola Virtual Gov (ENAP):** Extração e descompactação dupla (`.tar.gz` contendo `.gzip` interno) lidando com separadores não padronizado (`|`).
- Processamento direto em memória RAM (`io.BytesIO`), com eliminação de arquivos físicos locais (Zero disco).

---

### 🔹 Micro-Batching & Gestão de Memória

- Processamento de arquivos com **+2.3 milhões de linhas mensais**
- Arquitetura iterativa de carregamento em lotes
- Liberação imediata de memória após carga
- Prevenção de erros de Out Of Memory (OOM)

---

### 🔹 Conformidade com LGPD

- Pseudonimização determinística de CPF via **SHA-256**
- Hash aplicado antes do armazenamento
- Permite cruzamentos futuros mantendo anonimização
- Segurança aplicada já na camada Bronze

---

### 🔹 Auditoria e Rastreabilidade

- Logs estruturados com biblioteca `logging`
- Registro de:
  - Horário de execução
  - Volume processado
  - Falhas HTTP (ex: 404)
  - Status de carga no BigQuery
- Pipeline rastreável ponta a ponta

---

## 📊 Desafios Técnicos Resolvidos

- Processamento de grandes volumes (milhões de linhas) sem estouro de memória (OOM).
- Resolução de compactação oculta em arquivos governamentais (arquivos GZIP escondidos dentro de pacotes TAR).
- Anonimização determinística idempotente: o pipeline mantém o padrão SHA-256 mesmo ingerindo bases com diferentes níveis de mascaramento na origem (ex: MD5 pré-mascarado).
- Arquitetura escalável desenhada em documento formal (RFC/ADR) para evolução futura.

---

## 🛠️ Tecnologias Utilizadas

**Linguagem:** Python 3.13  
**Bibliotecas:** Pandas, SQLAlchemy, google-cloud-bigquery, requests, io, zipfile, tarfile, hashlib, logging  
**Banco Local:** PostgreSQL 15  
**Cloud Data Warehouse:** Google BigQuery  
**Containerização:** Docker  
**Modelagem (em andamento):** dbt + SQL  

---

## 📁 Estrutura do Repositório

- `fase1_local_postgres/` → Ingestão inicial e diagnóstico local.
- `fase2_cloud_bigquery/` → Ingestão automática Cloud Native.
- `PROPOSTA_ARQUITETURA_MAPEAMENTO.md` → Desenho arquitetural, premissas, riscos e trade-offs do ecossistema.
- `RELATORIO_DIAGNOSTICO.md` → Relatório técnico de qualidade de dados.
- Scripts `.py` → Automação e carga de dados.

---

## 🎯 Objetivo Arquitetural

Construir uma base de dados pública estruturada, segura e escalável, preparada para:

- Modelagem analítica avançada
- Governança de dados
- Criação de indicadores estratégicos
- Aplicações futuras de Data Science

---

**Desenvolvido por Ediney Magalhães**  
Data & Analytics Engineering Project | Cloud Data Architecture
