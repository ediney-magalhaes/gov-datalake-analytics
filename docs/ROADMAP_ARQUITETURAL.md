# Roadmap — Data Lake Analytics GOV
### Plataforma de Análise de Pessoal da Administração Pública Federal
**Motivação:** PNUD BRA/21/011 — MGI/SETE/SGP  
**Última atualização:** 11/07/2026

---

## 1. Visão Geral do Projeto

Este projeto implementa uma **Plataforma de Dados Governamental** para consolidação, tratamento e análise da força de trabalho do Poder Executivo Federal, abrangendo quatro editais promovidos pelo PNUD em parceria com o MGI.

**Arquitetura:** Medallion (Bronze → Silver → Gold), implementada em Google Cloud Platform (GCS + BigQuery), orquestrada pelo Dagster e transformada via dbt Core.

**Bases de dados:** SIAPE, DEPRO, ENAP, Observatório de Pessoal, PEP, ACT Lemann, Pesquisa Vozes, Base de Currículos.

**Princípios norteadores:**
- Segurança First: pseudonimização LGPD (SHA-256 + Salt) aplicada in-flight
- Analytics as Code: todo o fluxo versionado em Git
- Idempotência: reprocessamento sem duplicidade
- FinOps: particionamento Hive e clustering BigQuery para controle de custos

> Para detalhamento arquitetural completo, consulte `PROPOSTA_ARQUITETURA_MAPEAMENTO.md`.

---

## 2. Estrutura de Trilhas

O projeto opera em quatro trilhas com dependência em cascata:

```
Trilha A — Plataforma de Dados (Edital 01)
    └── alimenta
Trilha B — Estudos Analíticos: Remuneração e Trajetórias (Edital 02)
Trilha C — Estudos Analíticos: Competências e Diversidade (Edital 04)
    └── B e C concluídas alimentam
Trilha D — Supervisão e Integração Final (Edital 03)
```

**Trilhas B e C** são paralelas e independentes entre si, mas complementares no resultado final. Ambas dependem da Gold (Trilha A).  
**Trilha D** é ativada somente após a conclusão de B e C.

---

## 3. Estado Atual

### 3.1 Visão Macro por Fase

| Fase | Trilha | Descrição | Status | Atualizado em |
|:-----|:-------|:----------|:------:|:-------------:|
| Fase 0 | A | Auditoria Arquitetural da Camada Bronze | ✅ Concluída | Mar/2026 |
| Fase 1 | A | Expansão da Camada Bronze | ✅ Concluída | Jul/2026 |
| Fase 2 | A | Estabilização da Ingestão | ⏸️ Diferida (ADR-016) | Jul/2026 |
| Fase 3 | A | Reconstrução da Camada Silver (dbt) | 🔄 Em andamento | Jul/2026 |
| Fase 4 | A | Reconstrução da Camada Gold (Data Marts) | ⏳ Pendente | — |
| Fase 5 | A | Infraestrutura como Código e CI/CD | ⏳ Pendente | — |
| Fase 6 | A | Observabilidade e FinOps | ⏳ Pendente | — |
| Bloco 1 | B | Estudos: Remuneração e Trajetórias (Edital 02) | ⏳ Aguarda Gold | — |
| Bloco 2 | C | Estudos: Competências e Diversidade (Edital 04) | ⏳ Aguarda Gold | — |
| Bloco 3 | D | Supervisão e Integração Final (Edital 03) | ⏳ Aguarda B e C | — |

---

### 3.2 Detalhamento por Fase

---

#### TRILHA A — Plataforma de Dados (Edital 01)

---

##### ✅ Fase 0 — Auditoria Arquitetural da Camada Bronze
**Objetivo:** Garantir que a fundação suporte ingestão massiva de 10+ anos de histórico.

| Sprint | Entrega | Status |
|:-------|:--------|:------:|
| 0.1 | Divisão lógica Bronze Raw / Bronze Normalized | ✅ |
| 0.2 | Padronização de estrutura de pastas (Hive Partitioning) | ✅ |
| 0.3 | Motor de ingestão (Polars) com pseudonimização LGPD in-flight | ✅ |
| 0.4 | Metadados universais e naming conventions (snake_case, Regex) | ✅ |
| 0.5 | ADRs 009–014 registradas | ✅ |

---

##### ✅ Fase 1 — Expansão da Camada Bronze
**Objetivo:** Ingestão completa de todas as bases estruturantes com backfill histórico (2015–2026).

| Sprint | Entrega | Status |
|:-------|:--------|:------:|
| 1.1 | Assets Dagster: SIAPE (ativos, remuneração, aposentados, afastamentos) | ✅ |
| 1.2 | Assets Dagster: DEPRO (alocação, cargos, aposentadorias) | ✅ |
| 1.3 | Asset Dagster: ENAP (matrículas) com dupla descompactação TAR.GZ | ✅ |
| 1.4 | Particionamento mensal: 136 partições por asset (2015-01 a 2026-04) | ✅ |
| 1.5 | Integração GCS: motor de ingestão com destino configurável via `.env` | ✅ |
| 1.6 | Bucket `gov-datalake-analytics-bronze` provisionado (us-east1, Standard) | ✅ |
| 1.7 | Teste de escrita GCS validado: SIAPE Ativos jan/2025 (55MB raw + 55MB normalized) | ✅ |
| 1.8 | Backfill histórico completo — 8 assets × 136 partições | ✅ |
| 1.9 | Asset: PEP via Base dos Dados (BigQuery público) | ⏳ Pendente — não-bloqueante |
| 1.10 | Backfill histórico ENAP — cache local + `pl.scan_csv()` lazy + download manual (bloqueio anti-bot do servidor) | ✅ |
| 1.11 | Merge branch `feature/integracao-gcs` na main | ✅ |

**Bloqueios ativos:**
- Nenhum bloqueio técnico ativo na Fase 1.

**Nota de escopo (18/07/2026):** Investigação confirmou que "Observatório de Pessoal" e "PEP" são a mesma fonte (o Observatório é o portal, o PEP é o dado); consolidados em um único item. "ACT Lemann" foi identificado como produto analítico pronto (resultado de Acordo de Cooperação Técnica MGI + Fundação Lemann), sem estrutura tabular ou chave de cruzamento — reclassificado como insumo do Produto 2 (Fundamentação Teórico-Conceitual, Edital 04) e removido do escopo de ingestão Bronze.

---

##### ⏸️ Fase 2 — Estabilização da Ingestão (Diferida)
**Objetivo:** Confiabilidade operacional antes de promover dados para Silver.

Entregas previstas: validação de contract drift (mudanças de schema na origem), controle de volumetria, logs estruturados (JSON).

**Status:** Diferida para execução em paralelo com a Fase 3, conforme ADR-016. Bug de dual logging já corrigido em 26/04/2026 (consolidação do motor de ingestão em `resources/motor_ingestao.py` com logging centralizado) — item mantido nesta seção apenas por rastreabilidade histórica. Retomada condicionada a: nova execução do pipeline de ingestão, ou necessidade identificada ao final da Camada Gold.

**Dependência:** Fase 1 concluída.

---

##### 🔄 Fase 3 — Reconstrução da Camada Silver (dbt Core)
**Objetivo:** Modelagem dimensional (Kimball) sobre a Camada Bronze homologada, aplicando a estratégia de chave definida na ADR-009.

| Sprint | Entrega | Status |
|:-------|:--------|:------:|
| 3.1 | Inicialização do projeto dbt Core — `profiles.yml` conectado ao BigQuery | ✅ Concluído |
| 3.2 | Primeira validação de conexão — `dbt debug` bem-sucedido | ✅ Concluído |
| 3.3 | Modelos de staging (`stg_`) — 8 assets (SIAPE ×4, DEPRO ×3, ENAP ×1), aplicando `id_servidor_portal` como chave de cruzamento (ADR-009). ENAP tratada como fato independente, sem linkage com SIAPE/DEPRO (ver correção da ADR-009 em 02/08/2026) | ✅ Concluído |
| 3.4 | Definição de testes dbt (`unique`, `not_null`, `relationships`) nos modelos de staging | ⏳ Pendente |
| 3.5 | Modelagem dimensional Kimball — definição de dimensões e fatos para os Tracks B e C. Inclui PEP como fato independente (base agregada por grupo demográfico/organizacional, sem identificação individual — não participa do JOIN via `id_servidor_portal`). Avaliar reaproveitamento de `stg_siape__aposentados` para os Estudos 3 (Fluxos e Fronteiras) e 4 (Contratações Temporárias): a tabela contém 45 categorias de `situacao_vinculo`, incluindo cessão (2,2M+ linhas) e contratação temporária (1,4M+ linhas), não só aposentadoria (29,9M linhas) — descoberto na Sprint 3.4 (06/08/2026). `stg_siape__afastamentos` tem 173 linhas (0,002% do total) com `data_inicio_afastamento` e `data_fim_afastamento` ambas nulas — excluir esses registros ao construir a Mart/Fato de Afastamentos, não representam afastamento válido — descoberto na Sprint 3.4 (06/08/2026) | ⏳ Pendente |

**Dependência:** Fase 1 concluída (✅), ADR-009 aceita (✅). Fase 2 diferida (ADR-016) — não bloqueia o início da Fase 3.

**Bloqueios ativos:** Nenhum.

---

##### ⏳ Fase 4 — Reconstrução da Camada Gold (Data Marts)
**Objetivo:** Modelos analíticos definitivos para consumo nos estudos e no Power BI.

Entregas previstas: OBT por tema (Trajetórias, Remuneração, Diversidade, Competências, Aposentadorias, Capacitação), particionamento `PARTITION BY mes_referencia`, clustering `CLUSTER BY orgao, uf, hash_cpf`, decisão FinOps External Tables vs tabelas nativas (ADR pendente).

**Dependência:** Fase 3 concluída.

---

##### ⏳ Fase 5 — Infraestrutura como Código e CI/CD
**Objetivo:** Gerenciar infraestrutura GCP de forma auditável e automatizar o ciclo de vida do dado.

Entregas previstas: Terraform para buckets, datasets e Service Accounts; GitHub Actions para CI (dbt test em PRs) e CD (deploy para produção); GitHub Secrets e Secret Manager.

**Dependência:** Fase 4 concluída.

---

##### ⏳ Fase 6 — Observabilidade e FinOps
**Objetivo:** Monitoramento de saúde, qualidade e custos em produção.

Entregas previstas: dashboards de custo BigQuery, alertas de latência e falha de pipelines, monitoramento de data drift.

**Dependência:** Fase 5 concluída.

---

#### TRILHA B — Estudos Analíticos: Remuneração e Trajetórias (Edital 02)

**Dependência:** Gold (Fase 4 da Trilha A) concluída.

| Produto | Descrição | Status |
|:--------|:----------|:------:|
| Produto 1 | Relatório de Diagnóstico e Formulação Analítica | ⏳ Pendente |
| Produto 2 | Relatório de Fundamentação Teórico-Conceitual | ⏳ Pendente |
| Produto 3 | Plano de Trabalho e Metodologia Validada | ⏳ Pendente |
| Produto 4 | Estudo 1: Trajetórias no SPF — Análise de Coorte (sobrevivência, Markov) | ⏳ Pendente |
| Produto 5 | Estudo 2: Modelagem Preditiva de Gastos com Pessoal e Aposentadorias | ⏳ Pendente |
| Produto 6 | Estudo 3: Fluxos e Fronteiras — Mobilidade Funcional e Institucional | ⏳ Pendente |
| Produto 7 | Estudo 4: Contratações Temporárias — Séries Temporais e Quebras Estruturais | ⏳ Pendente |
| Produto 8 | Relatório Final e Recomendações Estratégicas | ⏳ Pendente |

---

#### TRILHA C — Estudos Analíticos: Competências e Diversidade (Edital 04)

**Dependência:** Gold (Fase 4 da Trilha A) concluída. Paralela à Trilha B.

| Produto | Descrição | Status |
|:--------|:----------|:------:|
| Produto 1 | Relatório de Diagnóstico e Formulação Analítica | ⏳ Pendente |
| Produto 2 | Relatório de Fundamentação Teórico-Conceitual | ⏳ Pendente |
| Produto 3 | Plano de Trabalho e Metodologia Validada | ⏳ Pendente |
| Produto 4 | Estudo 1: Competências no SPF — Mapeamento, Alinhamento e Lacunas | ⏳ Pendente |
| Produto 5 | Estudo 2: Competências para Entregar Resultados — Alinhamento Estratégico | ⏳ Pendente |
| Produto 6 | Estudo 3: Diversidade e Desigualdades — Análise Interseccional | ⏳ Pendente |
| Produto 7 | Estudo 4: Quem Lidera o Estado? — Perfil e Diversidade das Lideranças | ⏳ Pendente |
| Produto 8 | Relatório Final e Recomendações Estratégicas | ⏳ Pendente |

---

#### TRILHA D — Supervisão e Integração Final (Edital 03)

**Dependência:** Trilhas B e C concluídas. Não iniciada.

Papel: supervisão técnica da integração dos resultados analíticos das Trilhas B e C, validação metodológica final e entrega consolidada ao MGI/SETE/PNUD.

---

## 4. Próximos Passos

Ações imediatas desbloqueadas hoje (02/08/2026):

1. **Sprint 3.4** — definição de testes dbt (`unique`, `not_null`, `relationships`, `accepted_values`) nos 8 modelos de staging já construídos
2. **Sprint 1.9** — iniciar levantamento das bases Observatório de Pessoal, PEP e avaliar disponibilidade da ACT Lemann
3. **Termo de Homologação da Prata** — aguardar conclusão das Sprints 3.4 e 3.5 antes de formalizar (não documentar parcialmente)
4. **Silver Layer** — iniciar modelagem dimensional Kimball e configuração do dbt Core, condicionada à decisão do item 1

---

## 5. Pendências Estratégicas de Longo Prazo

| Pendência | Contexto |
|:----------|:---------|
| Produto 1 — Edital 01 | Relatório de diagnóstico das bases não foi formalmente finalizado. Sessão de Documentação Reversa planejada ao final da Camada Gold. |
| Disponibilidade ACT Lemann | Acesso à base não confirmado. |
| Record Linkage ENAP | Confirmado em 02/08/2026 (ADR-009): `codigo_pessoa` é ID proprietário da EV.G, sem relação com CPF. ENAP não participa do JOIN nível-servidor com SIAPE/DEPRO. Estudos de capacitação (Trilhas B/C) ficam limitados a análises agregadas, salvo decisão futura por linkage probabilístico com validação de precisão. |


---

## 6. Gestão de Riscos Técnicos e Mitigações

|Risco Técnico | Impacto | Mitigação Implementada |
|:--- |:--- |:--- |
| **Bloqueio por Rate Limit (Erro 403)** | Alto | Pausas estruturadas e headers simulando navegadores reais. |
| **Inconsistência de schemas (Colunas)** | Médio | Filtro `Regex (Whitelist)` e isolamento da camada Bronze Normalized. |
| **Estouro de Memória (OOM)** | Alto | Motor vetorizado Polars — processamento colunar in-memory sem carregar o arquivo inteiro na RAM. |
| **Instabilidade de APIs e Firewalls (Timeouts, Erros 5xx)** | Alto | Blocos `try...except` e Graceful Degradation no motor de ingestão próprio. |
| **Duplicidade de registros** | Médio | "Chave composta, particionamento `Overwrite` e `dbt tests`." |
| **Custo excessivo de processamento** | Alto | `Hive Partitioning` no Data Lake e `Clustering` no BigQuery (FinOps). |
| **Mudança de schema na origem (Contract Drift)** | Médio | Detecção planejada para Fase 2 — validação de colunas a cada ingestão. |
| **Separador/encoding incorreto na origem (DEPRO)** | Alto | Descoberto em 02/08/2026 durante construção da Silver: os 3 CSVs do DEPRO usam `,` e `utf-8`, não `;`/`latin1` como documentado originalmente. Corrigido no código de ingestão (`depro.py`) e partições históricas reprocessadas via backfill Dagster. Risco geral para o projeto: parâmetros de ingestão documentados devem ser tratados como hipótese até validados contra o cabeçalho real do arquivo de origem, não como fato assumido. |

---

*Documento de estado do projeto — atualizar a cada sessão de trabalho.*  
*Para visão arquitetural e decisões técnicas, consulte `PROPOSTA_ARQUITETURA_MAPEAMENTO.md` e os ADRs em `docs/adr/`.*
---
