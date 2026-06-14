# Proposta de Arquitetura de Pipelines de Dados

**Projeto:** Data Lake - Gestão de Pessoal (Governo Federal)  
**Objetivo:** Definição da arquitetura técnica do fluxo de dados (Ingestão -> Transformação -> Consumo), governança, modelagem e automação de entrega.

---

## 1. Visão Geral da Arquitetura

A solução adota o paradigma Medallion Architecture (Bronze -> Prata -> Ouro), implementado integralmente em ambiente Cloud Native (Google Cloud Platform), priorizando:

- Escalabilidade elástica e processamento colunar otimizado.
- Conformidade estrita com a LGPD (Lei Geral de Proteção de Dados).
- Implementação de práticas de FinOps para controle de custos.
- Governança de dados orientada a testes automatizados.

---

## 2. Camada Bronze — Ingestão e Resiliência

Responsável pela captura fiel dos dados da origem, preservando a rastreabilidade histórica e criando um backup físico e imutável no Data Lake. Para suportar a escala de múltiplos sistemas estruturantes sem elevar custos, a camada foi dividida logicamente em duas zonas:

- **Bronze Raw:** Persistência imutável e 100% fiel à origem (Evidência de Auditoria). Sem regras de negócio, focada apenas na extração resiliente e pseudonimização *in-flight*.
- **Bronze Normalized:** Padronização estrutural universal (conversão para `snake_case`, tipagem básica, adição de metadados como `ingestion_timestamp` e `source_system`, e harmonização da chave `hash_cpf`). Evita que a camada Prata gaste processamento com "higiene estrutural".

### Características Técnicas:
- **Motor de Extração:** Uso do motor próprio baseado em **Polars** (Apache Arrow) para processamento vetorizado in-memory de arquivos massivos (ZIP/CSV) e **Requests** para download HTTP resiliente com headers dinâmicos. Decisão registrada em ADR-015.
- **Orquestração:** **Dagster 1.13.2** como orquestrador central, com assets particionados mensalmente (2015–2026) e suporte a backfill histórico. Decisão registrada em ADR-012.
- **Persistência Física (Data Lake):** O dado pousa primeiramente no **Google Cloud Storage (GCS)** no formato colunar **Parquet**, garantindo alta compressão (~80%). Decisão registrada em ADR-014.
    - A organização física segue o padrão **Hive Partitioning (year=YYYY/month=MM)**, visando otimização de scans (Partition Pruning) e redução drástica de custos no BigQuery (FinOps).
- **Governança Operacional e Resiliência:** Rastreabilidade ponta a ponta garantida por logging estruturado. Falhas no firewall do Governo são mitigadas com tratamento de exceções (`try...except`) e *Graceful Degradation*.

### Segurança (LGPD):
- Pseudonimização determinística (SHA-256) aplicada in-flight no CPF, **utilizando um 'Salt' criptográfico estático (gerenciado via variáveis de ambiente** `.env`) para mitigar riscos de engenharia reversa e ataques de força bruta. Decisão registrada em ADR-013.

---

## 3. Camada Prata — Transformação e Qualidade (dbt)

Responsável pela limpeza técnica, tipagem estrita e garantia de integridade histórica.

### Regras de Negócio e Engenharia:
- Tipagem de dados (DATE, NUMERIC, STRING) e padronização para snake_case.
- Deduplicação técnica: Uso de funções de janela (ROW_NUMBER) particionadas por hash_cpf, id_vinculo e mes_competencia.
- Observabilidade de Nulos: Imputação de valores padrão (ex: 'NAO INFORMADO') para manter a integridade da volumetria original da fonte.

### Validação de Qualidade:
Execução sistemática de dbt tests (Unique, Not Null, Accepted Values) em cada ciclo de transformação.

---

## 4. Camada Ouro — Consumo e Otimização (FinOps)

Planejada para alta performance analítica no Google BigQuery, atendendo aos blocos temáticos dos Editais 02 e 04.

### Estratégia de Modelagem e Integração:
- **OBT (One Big Table):** Adoção de tabelas analíticas consolidadas para reduzir a complexidade e o custo de JOINs no Power BI.
- **Integração Multi-fontes:** Cruzamento entre as bases do SIAPE, DEPRO e ENAP, garantido por chaves criptografadas unificadas (`hash_cpf`).

### Estratégia Colunar e FinOps:
- **Materialização Física:** As tabelas finais (*Data Marts*) serão materializadas fisicamente como `table` via dbt. Isso garante alta performance de leitura e previsibilidade de custos na nuvem, evitando o recálculo a cada consulta.
- **Particionamento e Clustering:** Adoção de `PARTITION BY mes_referencia` para otimização de scans (Partition Pruning) e `CLUSTER BY orgao, uf, hash_cpf` para acelerar filtros de busca.

### Governança e Qualidade:
- Contratos de dados e auditoria de qualidade (dbt tests) são aplicados no momento da transformação final, bloqueando inconsistências (ex: status fora do padrão ou nulos não tratados) antes da disponibilização no Data Lake.

---

## 5. Esteira de Entrega (CI/CD e DataOps)

A arquitetura prevê a implementação de integração e entrega contínua via GitHub Actions para garantir a confiabilidade do ciclo de vida do dado.

### Integração Contínua (CI):
- Gatilho automático a cada Push ou Pull Request.
- Execução automática de testes de schema e qualidade via dbt test.
- Bloqueio de integração caso falhas críticas de qualidade sejam detectadas.

### Entrega Contínua (CD):
- Deploy automatizado de modelos SQL para o ambiente de produção após aprovação dos testes.
- Gerenciamento de segredos e credenciais via GitHub Secrets.

---

## 6. Gestão de Riscos Técnicos e Mitigações

| Risco Técnico | Impacto | Mitigação Implementada |
|:--- |:--- |:--- |
| Bloqueio por Rate Limit (Erro 403) | Alto | Pausas estruturadas e headers simulando navegadores reais. |
| Inconsistência de nomes de colunas | Médio | Filtro de Regex (Whitelist) permitindo apenas caracteres alfanuméricos e _. |
| Estouro de Memória (OOM) | Alto | Motor vetorizado Polars (Apache Arrow) — processamento colunar in-memory sem carregar o arquivo inteiro na RAM. |
| Instabilidade de APIs Governamentais | Alto | Blocos `try...except` no motor de ingestão próprio para captura de erros de rede (Timeouts) e *Graceful Degradation*. |
| Duplicidade de registros | Médio | Chave composta e testes de unicidade automatizados no dbt. |
| Custo excessivo de processamento | Médio | Estratégias de particionamento e agrupamento físico no BigQuery. |
| Mudança de schema na origem (Contract Drift) | Médio | Detecção planejada para Fase 2 — validação de colunas a cada ingestão. |

---

## 7. Princípios Arquiteturais

1. **Segurança First:** Pseudonimização aplicada antes da persistência em nuvem.
2. **Arquitetura ELT:** Transformação realizada após o carregamento (Extract, Load, Transform).
3. **Idempotência:** Garantia de que reprocessamentos não gerem duplicidade ou corrupção de dados.
4. **Analytics as Code:** Todo o pipeline de transformação e teste é versionado e documentado.