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
| siape_afastamentos | 129 | 0,42 | 9.298.655 | ✅ Concluído |
| depro_alocacao | 60 | < 0,01 | 11.466 | ✅ Concluído |
| depro_cargos | 12 | < 0,01 | 142.404 | ✅ Concluído |
| depro_aposentadorias | 12 | < 0,01 | 257.547 | ✅ Concluído |
| enap_capacitacao | 132 | 0,54 | 19.346.163 | ✅ Concluído |
| **Total** | **741** | **17,34** | **276.470.183** | — |

---

## 5. Status do Backfill Histórico por Asset

| Asset | Período | Partições Raw | Partições Normalized | Status |
|:------|:--------|:-------------:|:--------------------:|:------:|
| siape_ativos | 2015–2025 | 132/132 | 132/132 | ✅ Concluído |
| siape_remuneracao | 2015–2025 | 132/132 | 132/132 | ✅ Concluído |
| siape_aposentados | 2015–2025 | 132/132 | 132/132 | ✅ Concluído |
| siape_afastamentos | 04/2015–2025 | 129/132 | 129/132 | ✅ Concluído |
| depro_alocacao | 2020-02 -> 2026-02 (c/ gaps) | 60/60 | 60/60 | ✅ Concluído |
| depro_cargos | 2024-02 → 2026-02 (c/ gaps) | 12/78 | 12/78 | ✅ Concluído |
| depro_aposentadorias | 2024-02 → 2026-02 (c/ gaps) | 12/78 | 12/78 | ✅ Concluído |
| enap_capacitacao | 2015–2025 | 132/132 | 132/132 | ✅ Concluído |

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

---

## 8. Riscos Conhecidos e Limitações Operacionais

### 8.1 Limitação de RAM (Concorrência)
**Sintoma:** `zipfile.BadZipFile` ao disparar múltiplas partições simultâneas.
**Causa:** Hardware local com 8GB RAM; execução concorrente de múltiplos processos do Dagster excede a memória disponível.
**Mitigação:** Configuração de `QueuedRunCoordinator` (max_concurrent_runs=1) via `DAGSTER_HOME` local (27/06/2026) — escopo cirúrgico de desbloqueio, não a migração completa de infraestrutura prevista na Fase 5.

### 8.2 Cooldown do Portal da Transparência
**Sintoma:** `zipfile.BadZipFile` em execuções rápidas (~7s), mesmo com concorrência limitada a 1.
**Causa:** Bloqueio temporário do servidor após múltiplas requisições consecutivas em curto intervalo (anti-bot).
**Mitigação:** Disparo em lotes de no máximo 6 partições, com pausa de alguns minutos entre lotes. Aplicável a todos os backfills futuros via Portal da Transparência (DEPRO, ENAP).
**Identificado em:** 27/06/2026, durante backfill de `siape_afastamentos`.

### 8.3 Dataset DEPRO inexistente antes de fevereiro/2020
**Sintoma:** `KeyError: 'alocacao-servidores.csv'` para a partição 2020-01.
**Causa:** O Raio-X da Administração Pública Federal foi lançado em janeiro de 2020, mas a dimensão de pessoal (`alocacao-servidores.csv`, `cargos-efetivos.csv`, `projecao-aposentadorias.csv`) só foi incluída a partir de fevereiro de 2020. O ZIP de 2020-01 contém apenas dados orçamentários.
**Impacto:** 1 partição indisponível por asset DEPRO. Série histórica inicia em 2020-02.
**Decisão:** Limitação da fonte — não há dado alternativo disponível. Registrado como gap estrutural.

### 8.4 Gap de publicação governamental — junho/2024 a junho/2025
**Sintoma:** HTTP 404 para partições de 2024-06 a 2025-06.
**Causa:** Interrupção de 13 meses na publicação dos ZIPs mensais do Raio-X, provavelmente associada à transição do Ministério da Economia para o MGI.
**Impacto:** 13 partições indisponíveis por asset DEPRO.
**Decisão:** Limitação da fonte — gap documentado, motor trata como skip silencioso via verificação de status 404.

### 8.5 Descontinuação do formato ZIP a partir de março/2026
**Sintoma:** `KeyError: 'alocacao-servidores.csv'` para partições de 2026-03 em diante.
**Causa:** A partir de março/2026, o governo alterou o modelo de publicação — os ZIPs passaram a conter novos arquivos (`pessoal-forca-trabalho.csv`, `carreira-cargo-efetivo-orgao.csv` etc.) sem os arquivos históricos de pessoal.
**Impacto:** Assets `depro_alocacao`, `depro_cargos` e `depro_aposentadorias` sem cobertura a partir de 2026-03.
**Decisão:** Limitação estrutural da fonte. Os novos arquivos serão avaliados como potenciais novos assets na próxima fase.
### 8.6 `cargos-efetivos.csv` inexistente no formato ZIP antes de fevereiro/2024
**Sintoma:** `KeyError: 'cargos-efetivos.csv'` para todas as partições de 2020-02 a 2024-01.
**Causa:** O arquivo `cargos-efetivos.csv` não fazia parte do formato original do Raio-X (v1.0.0 a v1.3.0). Foi incorporado ao pacote ZIP apenas a partir de fevereiro/2024, conforme verificado via inspeção do CHANGELOG.html e conteúdo dos ZIPs.
**Impacto:** Série histórica do `depro_cargos` inicia em 2024-02 — apenas 12 partições disponíveis.
**Decisão:** Limitação da fonte — não há dado alternativo disponível. Registrado como gap estrutural.