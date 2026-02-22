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

Responsável pela captura fiel dos dados da origem, preservando a rastreabilidade histórica sem persistência local intermediária.

### Características Técnicas:
- Extração via APIs públicas governamentais com tratamento de persistência em memória (io.BytesIO).
- Descompactação múltipla (ZIP, TAR.GZ, GZIP) em tempo de execução.
- Normalização de Schema (Whitelisting): Aplicação de Expressões Regulares (Regex) para garantir que 100% dos nomes de colunas sejam compatíveis com o padrão ANSI SQL.
- Mitigação de Bloqueios: Implementação de Rate Limiting e Headers customizados (User-Agent) para garantir a estabilidade das requisições junto aos servidores governamentais.

### Segurança (LGPD):
- Pseudonimização determinística (SHA-256) aplicada in-flight.
- Criptografia de dados sensíveis antes da persistência em nuvem.

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

Modelo otimizado para alta performance analítica no Google BigQuery.

### Estratégia Colunar:
- Adoção de OBT (One Big Table) para reduzir a complexidade e o custo de JOINs em grandes volumes.
- Particionamento Físico: PARTITION BY mes_referencia para otimização de scans (Partition Pruning).
- Agrupamento (Clustering): CLUSTER BY orgao, uf, hash_cpf para acelerar filtros de busca.

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

## 6. Matriz de Riscos Técnicos e Mitigações

| Risco Técnico | Impacto | Mitigação Implementada |
|:--- |:--- |:--- |
| Bloqueio por Rate Limit (Erro 403) | Alto | Pausas estruturadas (time.sleep) e headers simulando navegadores reais. |
| Inconsistência de nomes de colunas | Médio | Filtro de Regex (Whitelist) permitindo apenas caracteres alfanuméricos e _. |
| Estouro de Memória (OOM) | Alto | Processamento iterativo (micro-batching) e limpeza manual de cache (del df). |
| Duplicidade de registros | Médio | Chave composta e testes de unicidade automatizados no dbt. |
| Custo excessivo de processamento | Médio | Estratégias de particionamento e agrupamento físico no BigQuery. |

---

## 7. Princípios Arquiteturais

1. **Segurança First:** Pseudonimização aplicada antes da persistência em nuvem.
2. **Arquitetura ELT:** Transformação realizada após o carregamento (Extract, Load, Transform).
3. **Idempotência:** Garantia de que reprocessamentos não gerem duplicidade ou corrupção de dados.
4. **Analytics as Code:** Todo o pipeline de transformação e teste é versionado e documentado.