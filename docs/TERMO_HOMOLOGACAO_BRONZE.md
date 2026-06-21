# Termo de Homologação Técnica (UAT) - Camada Bronze

**Projeto:** Data Lake — Plataforma de Análise de Pessoal da Administração Pública Federal  
**Contrato:** PNUD BRA/21/011 — MGI/SETE/SGP  
**Fase:** Camada Bronze — Ingestão e Persistência Histórica  
**Status:** Em andamento — backfill parcial concluído  
**Última atualização:** 21/06/2026

---

## 1. Escopo da Homologação

Atesta-se a conclusão e o funcionamento automatizado da ingestão histórica na Camada Bronze (Google Cloud Storage), orquestrada pelo Dagster 1.13.2. O pipeline ingere dados do Portal da Transparência e os persiste em formato Parquet particionado por ano e mês (Hive Partitioning), em duas zonas distintas: `bronze_raw` (fidelidade absoluta à origem) e `bronze_normalized` (padronização estrutural mínima).

Os oito assets registrados e validados são:

| Asset | Sistema | Descrição |
|:------|:--------|:----------|
| siape_ativos | SIAPE | Cadastro funcional de servidores ativos |
| siape_remuneracao | SIAPE | Detalhamento de rubricas e pagamentos |
| siape_aposentados | SIAPE | Cadastro de aposentados e pensionistas |
| siape_afastamentos | SIAPE | Registro de afastamentos de servidores |
| depro_alocacao | DEPRO | Alocação de servidores por órgão |
| depro_cargos | DEPRO | Cargos de servidores por órgão |
| depro_aposentadorias | DEPRO | Projeção de aposentadorias por órgão |
| enap_capacitacao | ENAP | Matrículas e capacitação — Escola Virtual Gov |

---

## 2. Métricas de Performance e Stress Test

Durante a execução do pipeline de ingestão, o sistema registrou os seguintes indicadores de performance e resiliência:

- **Processamento em memória:** 100% via `io.BytesIO` — consumo de disco local: 0 bytes
- **Throughput médio observado:** 14.360 registros tratados e ingeridos por segundo
- **Tempo médio por partição:** ~40 segundos (medido no SIAPE Ativos)
- **Resiliência de Schema:** Validação via Regex (whitelist), garantindo conformidade de 100% dos nomes de colunas com o padrão snake_case/ANSI SQL
- **Evasão de Bloqueio (403):** Mitigação de bloqueios de firewall governamental via Rate Limiting e Headers dinâmicos
- **Destino:** Bucket GCS `gov-datalake-analytics-bronze` (us-east1, Standard)
- **Formato:** Parquet colunar com Hive Partitioning (`year=YYYY/month=MM`)

---

## 3. Conformidade Legal e Segurança (LGPD)

Validado o processo de pseudonimização in-flight. A coluna de identificação pessoal (CPF) de todas as bases foi convertida com sucesso em chaves criptográficas (SHA-256 + Salt estático gerenciado via variável de ambiente) na memória volátil, garantindo que nenhum dado sensível em texto claro seja persistido no armazenamento em nuvem.

Decisão arquitetural registrada em ADR-013 (`docs/adrs/0013-sha256-salt-estrategia-lgpd.md`).

---

## 4. Volumetria por Asset

Tabela atualizada progressivamente conforme conclusão do backfill histórico de cada asset.

| Asset | Arquivos Raw | Tamanho Raw (GB) | Registros | Status |
|:------|:-----------:|:----------------:|:---------:|:------:|
| siape_ativos | 132 | 6,90 | 100.659.967 | ✅ Concluído |
| siape_remuneracao | 132 | 4,46 | 68.693.388 | ✅ Concluído |
| siape_aposentados | 132 | 5,02 | 78.060.593 | ✅ Concluído |
| siape_afastamentos | — | — | — | ⏳ Pendente |
| depro_alocacao | — | — | — | ⏳ Pendente |
| depro_cargos | — | — | — | ⏳ Pendente |
| depro_aposentadorias | — | — | — | ⏳ Pendente |
| enap_capacitacao | — | — | — | ⏳ Pendente |
| **Total** | **396** | **16,38** | **247.413.948** | — |

---

## 5. Status do Backfill Histórico por Asset

| Asset | Período | Partições Raw | Partições Normalized | Status |
|:------|:--------|:-------------:|:--------------------:|:------:|
| siape_ativos | 2015–2025 | 132/132 | 132/132 | ✅ Concluído |
| siape_remuneracao | 2015–2025 | 132/132 | 132/132 | ✅ Concluído |
| siape_aposentados | 2015–2025 | 132/132 | 132/132 | ✅ Concluído |
| siape_afastamentos | 2015–2025 | — | — | ⏳ Pendente |
| depro_alocacao | 2015–2025 | — | — | ⏳ Pendente |
| depro_cargos | 2015–2025 | — | — | ⏳ Pendente |
| depro_aposentadorias | 2015–2025 | — | — | ⏳ Pendente |
| enap_capacitacao | 2015–2025 | — | — | ⏳ Pendente |

---

## 6. Evidências de Validação

- **Bucket GCS:** `gov-datalake-analytics-bronze`
- **Caminhos validados:**
  - `bronze_raw/siape_ativos/year=YYYY/month=MM/part-000.parquet`
  - `bronze_normalized/siape_ativos/year=YYYY/month=MM/part-000.parquet`
- **Orquestração:** Dagster 1.13.2 — 8 assets registrados, 132 partições mensais cada (2015-01 a 2025-12)
- **Repositório:** branch `main` (commits diretos pós-merge de `feature/integracao-gcs` e `refactor/dagster-home-idempotencia-granular-motor`)
- **ADRs relacionadas:** ADR-007, ADR-008, ADR-012, ADR-013, ADR-014

---

## 7. Assinaturas de Validação

- **Arquiteto/Engenheiro de Dados:** Ediney Magalhães Junior
- **Validação Técnica:** Evidência registrada via inspeção do bucket GCS e interface Dagster
- **Status Final:** Em andamento — homologação completa será emitida ao término do backfill histórico de todos os 8 assets