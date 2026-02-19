# 🏗️ Proposta de Arquitetura de Pipelines de Dados (Produto 1)

**Projeto:** Data Lake - Gestão de Pessoal (Governo Federal)
**Objetivo:** Desenho arquitetural do fluxo de dados (Ingestão à Exposição), definição de governança e mapeamento de riscos operacionais.

---

## 1. Visão Geral da Arquitetura Medallion

A solução adota o paradigma arquitetural *Medallion* (Bronze, Prata, Ouro) estruturado 100% em Cloud (*Google Cloud Platform*), visando escalabilidade, resiliência e foco no consumo colunar (*FinOps*).

* **Camada Bronze (Ingestão Bruta):** Scripts Python (`requests`, `pandas`, `google-cloud-bigquery`) extraem arquivos massivos das APIs do governo, processam em memória RAM (`io.BytesIO`) e carregam tabelas particionadas no BigQuery. A LGPD é garantida no "momento do voo" (Hash SHA-256).
* **Camada Prata (Limpeza e Histórico - Em construção):** Transformações via `dbt` (Data Build Tool). Limpeza de nulos, tipagem estrita de colunas e rastreamento de mudanças de cargo/órgão (SCD Tipo 2).
* **Camada Ouro (Consumo Analítico - Em construção):** Criação de uma *Wide Table* (OBT - One Big Table) desnormalizada, otimizada para ferramentas de BI, preterindo o *Star Schema* clássico para evitar custos de `JOINs` no banco colunar.

---

## 2. Fluxo ETL e Camadas de Ingestão

As três fontes validadas (SIAPE Ativos, SIAPE Aposentados e ENAP Capacitação) seguem um fluxo padronizado de orquestração:
1. **Trigger:** `00_orquestrador_bronze.py` aciona a malha de scripts sequenciais.
2. **Extract:** Requisição HTTP(s) com injeção de Headers (User-Agent) contornando WAFs (Firewalls) governamentais.
3. **Load (in-memory):** Descompactação dupla (ex: `.tar.gz` e `.zip`) diretamente na RAM, sem I/O de disco físico.
4. **Transform (Light/Security):** Aplicação unificada de criptografia `SHA-256` no CPF.
5. **Load (Destino):** Carga via Micro-batching no Google BigQuery.

---

## 3. Matriz de Riscos Técnicos e Mitigação

Para garantir a alta disponibilidade e resiliência exigidas no Edital, os seguintes riscos técnicos foram mapeados e já mitigados no Protótipo Funcional (Produto 2):

| Risco Técnico | Impacto | Estratégia de Mitigação Implementada |
| :--- | :--- | :--- |
| **Queda ou Bloqueio da API (Gov)** | Alto | Implementação de blocos `try/except`, tolerância de *timeout* (120s) e *User-Agent* dinâmico. Logs registram Status `404` ou `500` sem quebrar o pipeline (Fail-Safe). |
| **Estouro de Memória (OOM)** | Alto | Arquitetura de processamento iterativo (mês a mês) com lixeiro de RAM (`del df_mes`) acionado imediatamente após cada commit no banco. |
| **Vazamento de PII (Dados Pessoais)** | Gravíssimo | Nenhuma máquina local salva arquivos `.csv` brutos. O Hash `SHA-256` ocorre em variáveis transitórias antes do envio criptografado à nuvem. |
| **Gasto Excessivo em Cloud (FinOps)** | Médio | Tabelas criadas com regra incremental (`WRITE_APPEND` / `MERGE`), evitando reprocessamento full da base a cada nova execução. |

## 💰 Considerações de FinOps

A arquitetura prioriza:

- Processamento incremental (evitando full refresh desnecessário)
- Particionamento físico por mês de competência
- Clusterização para redução de leitura colunar
- Evitar JOINs excessivos na Camada Ouro (uso de OBT)

Essas decisões reduzem custo por query e mantêm previsibilidade orçamentária.

---

## 4. Seção de Governança e Decisões de Modelagem (Fase 3)

* **Data Lineage:** O rastreamento de origem (Source -> Bronze -> Prata -> Ouro) será documentado e gerado visualmente pelo framework `dbt docs`.
* **Política de Retenção:** Camada Bronze atua como arquivo morto imutável (*append-only* ou *truncate* controlado).
* **Particionamento:** A Camada Ouro (OBT) será particionada por `mes_referencia` (`PARTITION BY`) e clusterizada (`CLUSTER BY`) por `orgao`, `uf` e `hash_cpf`.
* **Granularidade (Fato):** 1 linha por servidor ativo/inativo por mês de competência, viabilizando o histórico acumulado exato sem explosão de cardinalidade.