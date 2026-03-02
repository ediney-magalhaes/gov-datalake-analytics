# Projeto Data Lake - Gestão de Pessoal (Governo Federal)

Projeto técnico de Arquitetura de Dados em Cloud para ingestão, tratamento e disponibilização de dados públicos do Governo Federal (folha de pagamento, aposentadorias e capacitação do executivo federal).

O projeto como um todo abrangerá o desenvolvimento de processos de governança e de infraestrutura digital pública que garantam a interoperabilidade, a atualização contínua e o uso analítico das informações, no âmbito da Secretaria Extraordinária para a Transformação do Estado (SETE) e da Secretaria de Gestão de Pessoas (SGP), vinculada ao Projeto BRA/21/011 – Fortalecimento de Capacidades para Modernização e Aprimoramento da Gestão Estatal da União.

---

## Contexto e Desafio de Negócio

O Poder Executivo Federal gera diariamente uma vasta quantidade de dados sobre a gestão de seus servidores. Historicamente, essas informações encontram-se dispersas em múltiplos sistemas (SIAPE, SouGov, SIAPEcad, SIGEPE, entre outros), com estruturas heterogêneas e limitada interoperabilidade, o que dificulta análises consistentes e o uso em tempo real para subsidiar decisões.

### O Problema
A extração manual ou semiautomatizada dessas bases fragmentadas compromete a agilidade, confiabilidade e abrangência das análises, ressaltando a necessidade de desenvolvimento de soluções integradas, automatizadas e seguras, que promovam a unificação das bases de dados e facilitem a governança da informação no âmbito do governo federal.

### A Solução
Em alinhamento com a Estratégia Federal de Governo Digital (Portaria SGD/MGI nº 6.618/2024), este projeto constrói uma infraestrutura digital pública unificada. Adotando princípios inspirados na arquitetura medallion (camadas bronze, silver e gold), que organiza os dados em níveis crescentes de qualidade e tratamento: desde a ingestão bruta e imutável (bronze), passando por estruturas refinadas e confiáveis para análise (silver), até vistas analíticas consolidadas voltadas à tomada de decisão (gold).

O pipeline desenvolvido foca em resiliência e segurança:
- Automatiza a coleta de dados de múltiplas fontes oficiais (APIs paginadas e arquivos massivos).
- Cada etapa do pipeline incorpora mecanismos automatizados de anonimização ou pseudonimização de dados pessoais sensíveis, em conformidade com a LGPD, integrando esses procedimentos diretamente aos processos de ingestão e transformação.
- Entrega bases consolidadas para subsidiar análises preditivas, estudos de trajetórias funcionais, diversidade e mapeamento de competências.

---

## Decisões Arquiteturais - Fase 3 (Upgrade de Ingestão e Governança)

Para garantir a escalabilidade exigida e a aprovação em auditorias de conformidade, a arquitetura de ingestão (Camada Bronze) foi reestruturada adotando o padrão *Modern Data Stack*:

* **Processamento em Memória (Otimizado):** Substituição do Pandas pelo **Polars**. O processamento vetorizado evita erros de falta de memória (OOM) ao descompactar e ler dezenas de gigabytes de arquivos ZIP governamentais.
* **Framework de Extração (APIs):** Adoção do **dlt (Data Load Tool)** para automatizar, paralelizar e padronizar as requisições em APIs complexas (como SIAPEcad e SouGov). Implementação de resiliência de rede (Graceful Degradation) com blocos `try...except` para suportar instabilidades nos firewalls do Governo (Serpro).
* **Armazenamento Colunar (Data Lake):** Transição de bancos locais/memória para persistência física no formato **Parquet** via destino `filesystem` nativo do dlt. Isso garante alta compressão e atua como backup imutável da Camada Bronze, pronto para migração Cloud (Google Cloud Storage / AWS S3).
* **Segurança In-Flight (LGPD):** Implementação de Hashing Determinístico (SHA-256) na coluna CPF utilizando a biblioteca nativa `hashlib` durante o processamento in-memory, antes da persistência no disco.
* **Governança Operacional:** Implementação de **Dual Logging** (Terminal + `.log` local via biblioteca nativa `logging`), registrando a saúde, latência e falhas de cada extração, provendo total rastreabil
---

## Qualidade de Dados e Governança (Fases 1 e 2 - Legado do dbt)

A confiabilidade dos dados é monitorada por testes automatizados via dbt Core, garantindo uma transição segura entre as camadas:

- **Contratos de Dados (Camada Ouro):** Implementação de testes restritos (`accepted_values`) para garantir a padronização semântica.
- **Observabilidade de Nulos:** Testes de `not_null` identificaram inconsistências nas fontes primárias tratadas via regras de imputação (`COALESCE`).
- **Auditoria de Unicidade Complexa:** Implementação de testes de chave composta (`unique_combination_of_columns`) para evitar duplicação em tabelas de cruzamento financeiro.
- **Normalização de Schema:** Uso de Expressões Regulares (Regex) para limpeza de cabeçalhos.
- **Linhagem de Dados:** Documentação técnica gerada via `dbt docs` para rastreamento completo.

---

## Status do Projeto

| Fase | Arquitetura | Status | Entregáveis |
|------|------------|--------|------------|
| Fase 1 e 2 (Legado) | Python (Pandas) + PostgreSQL + BQ | Refatorada | Ingestão inicial, provas de conceito e diagnósticos. |
| Fase 3 (Upgrade Ingestão) | Polars + dlt + DuckDB + Parquet | Em Execução | Performance in-memory, LGPD automatizada e Dual Logging. |
| Fase 4 (Cloud - Prata) | BigQuery + dbt Core | Concluída | Modelagem Staging, Tipagem Estrita e Testes de Qualidade. |
| Fase 5 (Cloud - Ouro) | BigQuery + dbt Core | Concluída | Data Marts, materialização e contratos de dados. |

---

## Tecnologias Utilizadas

- **Linguagem:** Python 3.12 LTS.
- **Processamento Big Data:** Polars, DuckDB, Apache Arrow.
- **Ingestão de APIs:** dlt (Data Load Tool), Requests.
- **Segurança e Governança:** Hashlib (SHA-256), Logging Nativo.
- **Transformação e Qualidade:** dbt Core (Data Build Tool).
- **Armazenamento:** Google BigQuery, Cloud Storage (Formato Parquet).

---

## Como Executar (Pipeline de Ingestão)

### 1. Pré-requisitos
- Python 3.12 ou superior.
- Service Account do Google Cloud com permissões de BigQuery Data Editor.

### 2. Configuração de Ambiente
```bash
# Definir variável de ambiente para autenticação
export GOOGLE_APPLICATION_CREDENTIALS="caminho/para/sua-chave.json"
```

### 3. Execução da Ingestão
```bash
python fase_2/14_ingestao_remuneracao_bronze.py
```

### 4. Para gerar e visualizar o dicionário de dados e a linhagem:
```bash
dbt docs generate
dbt docs serve
```

---

## Estrutura do Repositório
```bash
/
├── docs/                     # Documentação técnica, Dicionários e Homologações.
├── legado_pandas/            # Scripts das Fases 1 e 2 (Arquivados para histórico).
├── fase3_upgrade_ingestao/   # Scripts de Ingestão de Alta Performance (Polars/dlt).
├── analytics_gov/            # Projeto dbt (Modelos Prata, Ouro e Testes de Qualidade).
├── .gitignore                # Regras de segurança para ocultar .venv, .parquet e .log.
├── CONTRIBUTING.md           # Políticas de Versionamento e Commits.
└── README.md
```

**Ediney Magalhães**

Engenharia de Dados e Analytics
/Arquitetura de Dados em Nuvem

---