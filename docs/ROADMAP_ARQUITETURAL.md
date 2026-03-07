# Roadmap Arquitetural — Data Lake Analytics GOV

Este documento define a evolução planejada da arquitetura do projeto, organizando as fases técnicas e as próximas decisões estruturantes.

O objetivo é garantir maturidade progressiva da solução, alinhando:

- Escalabilidade

- Governança

- Conformidade (LGPD)

- Performance

- Sustentabilidade (FinOps)

- Reprodutibilidade (DataOps)


---



## 1. Histórico de Evolução (Fases Concluídas / Em Refatoração)

### 1.1 Visão Geral da Arquitetura

A solução adota o paradigma Medallion Architecture (Bronze -> Prata -> Ouro), implementado integralmente em ambiente Cloud Native (Google Cloud Platform), priorizando:

- Escalabilidade elástica e processamento colunar otimizado.
- Conformidade estrita com a LGPD (Lei Geral de Proteção de Dados).
- Implementação de práticas de FinOps para controle de custos.
- Governança de dados orientada a testes automatizados.

---

### 1.2 Camada Bronze — Ingestão e Resiliência (Modern Data Stack)

Responsável pela captura fiel dos dados da origem, preservando a rastreabilidade histórica e criando um backup físico e imutável no Data Lake.

#### Características Técnicas:
- **Motores de Extração Híbridos:** Uso do motor **Polars** (Apache Arrow) para processamento vetorizado in-memory de arquivos massivos (ZIP/CSV), e do framework **dlt (Data Load Tool)** para extração automatizada, resiliente e paginada de APIs governamentais complexas.
- **Persistência Física (Data Lake):** O pipeline não envia dados brutos direto para o Data Warehouse. O dado pousa primeiramente em Cloud Storage (ou sistema de arquivos local) no formato colunar **Parquet**, garantindo alta compressão (~80%) e backup histórico imutável.
    - A organização física no Data Lake segue o padrão **Hive Partitioning (year=YYYY/month=MM)**, visando otimização de scans (Partition Pruning) e redução drástica de custos no BigQuery (FinOps).
- **Normalização de Schema:** Aplicação de Expressões Regulares (Regex) in-flight para garantir que 100% dos nomes de colunas sejam compatíveis com o padrão ANSI SQL.
- **Governança Operacional e Resiliência:** Rastreabilidade ponta a ponta garantida por **Dual Logging** (Terminal + arquivo físico `.log`) via biblioteca nativa `logging`, atendendo aos requisitos estritos de auditoria. Falhas no firewall do Governo são mitigadas com tratamento de exceções (`try...except`) e *Graceful Degradation*.

#### Segurança (LGPD):
- Pseudonimização determinística (SHA-256) aplicada in-flight no CPF, **utilizando um 'Salt' criptográfico estático (gerenciado via variáveis de ambiente** `.env`) para mitigar riscos de engenharia reversa e ataques de força bruta.

---

### 1.3 Camada Prata — Transformação e Qualidade (dbt)

Responsável pela limpeza técnica, tipagem estrita e garantia de integridade histórica.

#### Regras de Negócio e Engenharia:
- Tipagem de dados (DATE, NUMERIC, STRING) e padronização para snake_case.
- Deduplicação técnica: Uso de funções de janela (ROW_NUMBER) particionadas por hash_cpf, id_vinculo e mes_competencia.
- Observabilidade de Nulos: Imputação de valores padrão (ex: 'NAO INFORMADO') para manter a integridade da volumetria original da fonte.

#### Validação de Qualidade:
Execução sistemática de dbt tests (Unique, Not Null, Accepted Values) em cada ciclo de transformação.

---

### 1.4 Camada Ouro — Consumo e Otimização (FinOps)

Modelo totalmente implementado e otimizado para alta performance analítica no Google BigQuery, atendendo aos blocos temáticos do Produto 4 do Edital.

#### Estratégia de Modelagem e Integração:
- **OBT (One Big Table):** Adoção de tabelas analíticas consolidadas para reduzir a complexidade e o custo de JOINs no Power BI.
- **Integração Multi-fontes:** Cruzamento validado entre as bases do SIAPE e ENAP, garantido por chaves criptografadas unificadas (`hash_cpf`).

#### Estratégia Colunar e FinOps:
- **Materialização Física:** As tabelas finais (*Data Marts*) foram materializadas fisicamente como `table` via dbt. Isso garante alta performance de leitura e previsibilidade de custos na nuvem, evitando o recálculo a cada consulta.
- **Particionamento e Clustering (Planejado para escala):** Adoção de `PARTITION BY mes_referencia` para otimização de scans (Partition Pruning) e `CLUSTER BY orgao, uf, hash_cpf` para acelerar filtros de busca.

#### Governança e Qualidade:
- Contratos de dados e auditoria de qualidade (dbt tests) são aplicados no momento da transformação final, bloqueando inconsistências (ex: status fora do padrão ou nulos não tratados) antes da disponibilização no Data Lake.

---

## 2. Reestruturação Arquitetural

**Motivador da Mudança**: O projeto concluiu com sucesso a sua Prova de Conceito (PoC) ponta a ponta. Agora o projeto se expande de um "Pipeline de Dados" para uma Plataforma de Dados Governamental. Serão ingeridos 6 sistemas estruturantes simultâneos (SIAPE, SIAPEcad, SIGEPE, SouGov, Vozes, DEPRO) com mais de 10 anos de histórico cada.

**A Grande Decisão Arquitetural (Divisão da Camada Bronze)**:
Para evitar que a heterogeneidade dessas 6 fontes diferentes resulte em maiores custos de processamento no BigQuery e gere gargalos na transformação (dbt), a Camada Bronze foi dividida logicamente em duas zonas:
- **Bronze Raw**: Persistência imutável e 100% fiel à origem (Evidência de Auditoria). Sem regras de negócio, focada apenas na extração resiliente e pseudonimização `in-flight`.
- **Bronze Normalized**: Padronização estrutural mínima para reduzir o custo de transformação na camada Silver. Aqui ocorre a harmonização de schemas, padronização em `snake_case`, injeção de metadados técnicos (ex: `ingestion_timestamp`, `source_system`) e alinhamento de chaves (ex: `hash_cpf`). A camada Silver (Prata) deixa de fazer "higiene estrutural" e passa a focar apenas em regras de negócio analíticas.


---

## 2.1 Novo Roadmap de Escala da Plataforma
Este cronograma (estimado em 3 a 4 meses) foca em estabilizar completamente a ingestão antes de reativar as camadas analíticas.

**Fase 0 — Auditoria Arquitetural da Camada Bronze (Status: Em Andamento)**
- **Objetivo**: Garantir que a fundação suporte a ingestão massiva de 10+ anos.
- **Ações**: Implementar a segmentação lógica entre `Raw` e `Normalized`; Padronizar a estrutura de pastas (`/sistema/year=YYYY/month=MM/`); Garantir metadados universais e naming conventions.

**Fase 1 — Expansão da Camada Bronze**
- **Objetivo**: Ingestão completa de todas as bases estruturantes adicionais.
- **Ações**: Construir pipelines resilientes (Polars/dlt) para SIAPEcad, SIGEPE, SouGov Currículos, Pesquisa Vozes e Base DEPRO, salvando em Parquet particionado com hashing LGPD aplicado.

**Fase 2 — Estabilização da Ingestão**
- **Objetivo**: Confiabilidade operacional antes de ir para a nuvem
- **Ações**: Validação de ***contract drift*** (mudanças repentinas de colunas na origem do Governo), controle de volumetria e consolidação de logs estruturados (JSON).

**Fase 3 — Orquestração de Pipelines**
- **Objetivo**: Automatizar execução e gerenciar dependências.
- **Ações**: Implementar o **Dagster** como orquestrador central. Habilitar agendamentos (`scheduling`), retries automáticos para APIs instáveis e processamento de histórico massivo (Backfill).

**Fase 4 — Infraestrutura como Código e CI/CD (DataOps)**
- **Objetivo**: Gerenciar a infraestrutura cloud de forma auditável e automatizar o ciclo de vida do dado.
- **Ações (Terraform)**: Criar `buckets` do Data Lake, datasets do BigQuery e Service Accounts via código.
- **Ações (GitHub Actions - CI/CD)**:
    - ***Integração Contínua (CI)***: Gatilho automático a cada Pull Request rodando testes de schema (`dbt test`).
    - ***Entrega Contínua (CD)***: Deploy automatizado de modelos SQL para produção. Gerenciamento de senhas pelo GitHub Secrets e Secret Manager.

**Fase 5 — Reconstrução da Camada Silver (Prata)**
- **Objetivo**: Reestruturar os modelos intermediários usando o `dbt Core` para as 6 novas fontes.
- **Ações**: Construir `staging` padronizado, cruzar fontes usando a chave universal `hash_cpf`, aplicar deduplicação técnica avançada e validar a qualidade dos dados.

**Fase 6 — Reconstrução da Camada Gold (Ouro)**
- **Objetivo**: Modelar os Data Marts definitivos para consumo no Power BI.
- **Ações**: Consolidar tabelas OBT (One Big Table) para os temas: Trajetórias Funcionais, Diversidade, Aposentadorias, Capacitação e Clima Organizacional.

**Fase 7 — Observabilidade e FinOps**
- **Objetivo**: Monitoramento de saúde e custos em produção.
- **Ações**: Dashboards de custo do BigQuery, alertas de latência/falha de pipelines e acompanhamento de data drift.

**Fase 8 — Evolução Lakehouse (Visão Futura)**
- **Objetivo**: Aprimorar a integração direta entre Storage e Data Warehouse.
- **Ações**: Implementar `External Tables` no BigQuery lendo diretamente do Parquet no Cloud Storage (baixo custo de storage com alta performance de SQL).

---

## 2.2 Gestão de Riscos Técnicos e Mitigações

|Risco Técnico | Impacto | Mitigação Implementada |
|:--- |:--- |:--- |
| **Bloqueio por Rate Limit (Erro 403)** | Alto | Pausas estruturadas e headers simulando navegadores reais. |
| **Inconsistência de schemas (Colunas)** | Médio | Filtro `Regex (Whitelist)` e isolamento da camada Bronze Normalized. |
| **Estouro de Memória (OOM)** | Alto | "Uso do motor vetorizado Polars, processando gigabytes sem esgotar a RAM." |
| **Instabilidade de APIs (Timeouts)** | Alto | Framework `dlt` com blocos `try...except` e `Graceful Degradation`. |
| **Duplicidade de registros** | Médio | "Chave composta, particionamento `Overwrite` e `dbt tests`." |
| **Custo excessivo de processamento** | Alto | `Hive Partitioning` no Data Lake e `Clustering` no BigQuery (FinOps). |

---

## 2.3 Princípios Arquiteturais Norteadores
1. **Segurança First**: Pseudonimização irreversível (LGPD) aplicada `in-flight`, antes da persistência em disco ou nuvem.

2. **Arquitetura ELT**: Transformação (Regras de Negócio) realizada estritamente após o carregamento bruto no Data Warehouse.

3. **Idempotência Máxima**: Garantia de que reprocessar o pipeline 100 vezes gerará exatamente o mesmo resultado, sem duplicidade de dados.

4. **Analytics as Code**: Todo o fluxo (infraestrutura, extração, transformação e orquestração) é versionado em repositório Git.