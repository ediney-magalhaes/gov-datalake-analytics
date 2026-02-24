# Projeto Data Lake - Gestão de Pessoal (Governo Federal)

Projeto técnico de Arquitetura de Dados em Cloud para ingestão, tratamento e disponibilização de dados públicos do Governo Federal (folha de pagamento, aposentadorias e capacitação do executivo federal).

O objetivo é estruturar um Data Lake moderno em camadas (Bronze, Prata e Ouro), garantindo escalabilidade, governança, segurança e qualidade dos dados sob os princípios da Arquitetura Medallion.

---

## Contexto e Desafio de Negócio

O Poder Executivo Federal gera diariamente uma vasta quantidade de dados sobre a gestão de seus servidores. Historicamente, essas informações encontram-se dispersas em múltiplos sistemas heterogêneos (SIAPE, SouGov, SIAPEcad, etc.).

### O Problema
A extração manual ou semiautomatizada dessas bases fragmentadas compromete a agilidade, confiabilidade e interoperabilidade das informações, dificultando a visão estratégica e a tomada de decisão por parte do Ministério da Gestão e da Inovação (MGI).

### A Solução
Em alinhamento com a Estratégia Federal de Governo Digital (Portaria SGD/MGI nº 6.618/2024), este projeto constrói uma infraestrutura digital pública unificada. Utilizando a Arquitetura Medallion, o pipeline:

- Automatiza a coleta de dados de múltiplas fontes oficiais.
- Aplica anonimização (LGPD) in-flight via hashing determinístico.
- Entrega bases consolidadas e testadas para subsidiar painéis estratégicos.

---

## Métricas Técnicas e Impacto (Resultados Alcançados)

A arquitetura Cloud Native desenvolvida com processamento exclusivo em memória entregou resultados de performance e resiliência comprovados:

- **Volume Processado:** ~11,5 milhões de registros (SIAPE Ativos + SIAPE Aposentados + ENAP + SIAPE Remuneração).
- **Tempo Médio de Ingestão:** ~6,4 minutos (Fluxo completo Origem para BigQuery).
- **Throughput:** Pico de ~14.360 linhas/segundo durante a etapa de carga (load) no BigQuery (a média do job varia conforme I/O da fonte).
- **Consumo de Disco Local:** 0 bytes (Processamento 100% in-memory via io.BytesIO).
- **Resiliência de Rede:** Implementação de estratégias de Rate Limiting (pausas estruturadas) e Headers customizados para mitigação de erros 403 (Forbidden) em servidores governamentais.

---

## Qualidade de Dados e Governança (Fases 3 e 4)

A confiabilidade dos dados é monitorada por testes automatizados via dbt Core, garantindo uma transição segura entre as camadas Bronze, Prata e Ouro:

- **Contratos de Dados (Camada Ouro):** Implementação de testes restritos (como `accepted_values`) para garantir a padronização semântica das regras de negócio (ex: status de matrícula) e bloquear sujeiras da origem.
- **Observabilidade de Nulos:** Testes de `not_null` identificaram inconsistências nas fontes primárias (ex: temas de cursos ou campos de vínculo vazios). Essas ocorrências foram tratadas via regras de limpeza e imputação (uso de `COALESCE`).
- **Auditoria de Unicidade Complexa:** Implementação de testes de chave composta (`unique_combination_of_columns`) para garantir integridade matemática e evitar duplicação em tabelas de cruzamento financeiro e demográfico.
- **Normalização de Schema:** Uso de Expressões Regulares (Regex Whitelisting) no pipeline de ingestão para conformidade com os padrões SQL do BigQuery.
- **Linhagem de Dados:** Documentação técnica gerada via `dbt docs`, permitindo o rastreamento visual completo desde a origem até o modelo final de consumo.

---

## Status do Projeto

| Fase | Arquitetura | Status | Entregáveis |
|------|------------|--------|------------|
| Fase 1 (Local) | Docker + PostgreSQL + Python | Concluída | Ingestão inicial e diagnóstico de fontes. |
| Fase 2 (Cloud - Bronze) | BigQuery + Python | Concluída | Ingestão automatizada, Hash LGPD e Logs de Auditoria. |
| Fase 3 (Cloud - Prata) | BigQuery + dbt Core | Concluída | Modelagem Staging, Tipagem Estrita e Testes de Qualidade. |
| Fase 4 (Cloud - Ouro) | BigQuery + dbt Core | Concluída | Data Marts (Blocos 1, 2 e 3 do Edital), materialização FinOps e contratos de dados. |

---

## Arquitetura da Solução



1. **Fontes:** Portal da Transparência (SIAPE) e Escola Virtual Gov (ENAP).
2. **Ingestão:** Python (Extração em memória, Descompactação e SHA-256).
3. **Storage:** Google BigQuery (Camada Bronze).
4. **Transformação:** dbt / SQL (Camadas Prata e Ouro).
5. **Consumo:** Dashboards em Power BI e Looker Studio.

---

## Tecnologias Utilizadas

- **Linguagem:** Python 3.12 LTS.
- **Bibliotecas:** Pandas, Google Cloud BigQuery, Requests, Hashlib, Logging.
- **Transformação e Qualidade:** dbt Core (Data Build Tool).
- **Banco de Dados Cloud:** Google BigQuery.
- **Ambiente Local:** Docker e PostgreSQL.

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
├── docs/                 # Documentação técnica, Dicionários e Homologações.
├── fase_1/               # Scripts legados de ambiente local (Docker).
├── fase_2/               # Scripts de Ingestão Cloud (Python).
├── analytics_gov/        # Projeto dbt (Modelos Prata, Ouro e Testes).
├── .gitignore
├── CONTRIBUTING.md       # Políticas de Versionamento e Commits.
└── README.md
```

**Ediney Magalhães**
  Engenharia de Dados e Analytics
  Arquitetura de Dados em Nuvem
---