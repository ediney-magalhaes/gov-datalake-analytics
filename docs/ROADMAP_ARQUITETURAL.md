# Roadmap — Data Lake Analytics GOV
### Plataforma de Análise de Pessoal da Administração Pública Federal
**Motivação:** PNUD BRA/21/011 — MGI/SETE/SGP  
**Última atualização:** 07/08/2026

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
| Fase 3 | A | Reconstrução da Camada Silver (dbt) | ✅ Concluída | Ago/2026 |
| Fase 4 | A | Reconstrução da Camada Gold (Data Marts) | 🔄 Em andamento (Sprint 4.1/10 concluída) | Ago/2026 |
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

##### ✅ Fase 3 — Reconstrução da Camada Silver (dbt Core)
**Objetivo:** Modelagem dimensional (Kimball) sobre a Camada Bronze homologada, aplicando a estratégia de chave definida na ADR-009.
 
| Sprint | Entrega | Status |
|:-------|:--------|:------:|
| 3.1 | Inicialização do projeto dbt Core — `profiles.yml` conectado ao BigQuery | ✅ Concluído |
| 3.2 | Primeira validação de conexão — `dbt debug` bem-sucedido | ✅ Concluído |
| 3.3 | Modelos de staging (`stg_`) — 8 assets (SIAPE ×4, DEPRO ×3, ENAP ×1), aplicando `id_servidor_portal` como chave de cruzamento (ADR-009). ENAP tratada como fato independente, sem linkage com SIAPE/DEPRO (ver correção da ADR-009 em 02/08/2026) | ✅ Concluído |
| 3.4 | Testes dbt de qualidade nos 8 modelos de staging: 48 testes (`not_null`, `dbt_utils.accepted_range`), mapeados coluna a coluna contra os estudos dos editais. Decisão de não aplicar teste de unicidade em `stg_siape__ativos` formalizada em ADR-017 (vínculos concomitantes legítimos). Bugfix aplicado em `stg_siape__remuneracao` (linha de rodapé de CSV) | ✅ Concluído (06/08/2026) |
| 3.5 | Modelagem dimensional Kimball concluída: 8 fatos e 7 dimensões definidos e documentados em `docs/MODELO_DIMENSIONAL_GOLD.md`. Fatos: Remuneração, Vínculo/Ativos, Situação de Vínculo (reaproveitamento de `stg_siape__aposentados`, 45 categorias), Afastamentos, Cargos DEPRO, Aposentadorias Previstas DEPRO, Alocação DEPRO, Capacitação ENAP. Três bugs técnicos descobertos e corrigidos durante a sprint: duplicação exata em `stg_siape__afastamentos` (fix `DISTINCT`), anomalia de grão em `stg_depro__alocacao` (agregação `SUM`), inconsistência de tipo `idade`/`carga_horaria` em `stg_enap__capacitacao` (132 partições Bronze reescritas). PEP mantido como fato independente, conforme já decidido | ✅ Concluído (07/08/2026) |
 
**Dependência:** Fase 1 concluída (✅), ADR-009 aceita (✅). Fase 2 diferida (ADR-016), não bloqueou o andamento da Fase 3.
 
**Bloqueios ativos:** Nenhum.
 
**Documentos gerados nesta fase:** `docs/MODELO_DIMENSIONAL_GOLD.md` (insumo direto para a Fase 4), `docs/TERMO_HOMOLOGACAO_PRATA.md` (reescrito com dados reais das Sprints 3.4/3.5, ver Seção 5 deste roadmap para pendência de verificação residual), ADR-017.

---

##### 🔄 Fase 4 — Reconstrução da Camada Gold (Data Marts)
**Objetivo:** Modelos analíticos definitivos para consumo nos estudos e no Power BI, construídos a partir das decisões formalizadas em `docs/MODELO_DIMENSIONAL_GOLD.md`.
 
| Sprint | Entrega | Status |
|:-------|:--------|:------:|
| 4.1 | Dimensões compartilhadas: `dim_tempo`, `dim_servidor`, `dim_orgao_siape`, `dim_tipo_vinculo`, `dim_orgao_depro`, `dim_pessoa_enap`, `dim_curso_enap`. 7 dimensões construídas com SCD Tipo 1 nos atributos instáveis (identificados empiricamente, nao presumidos): `nome` (dim_servidor), `orgsup_lotacao` (dim_orgao_siape), praticamente todos os atributos de `dim_orgao_depro` (nenhum estável), `raca`/`uf_pessoa`/`municipio_pessoa`/`instituicao`/`poder`/`esfera` (dim_pessoa_enap), `nome_curso`/`conteudista`/`tematica` (dim_curso_enap). Configuração de schema por camada implementada (`macro generate_schema_name.sql` + `dbt_project.yml`, staging para `prata`, marts para `ouro`) | ✅ Concluído (08/08/2026) |
| 4.2 | Fato Remuneração (grão `id_servidor_portal + year + month`, sem chave surrogate) | ✅ Concluído (17/08/2026) |
| 4.3 | Fato Vínculo/Ativos (chave surrogate `sk_vinculo`, **8 colunas**, ADR-017 atualizado) | ✅ Concluído (21/08/2026) |
| 4.4 | Fato Situação de Vínculo (chave surrogate `sk_situacao_vinculo`, **7 colunas**, grão revalidado — não reaproveitou a chave de 8 colunas do ADR-017) | ✅ Concluído (21/08/2026) |
| 4.5 | Fato Afastamentos (grão `id_servidor_portal + year + month + datas`) | ⏳ Pendente |
| 4.6 | 3 Fatos DEPRO — Cargos, Aposentadorias Previstas, Alocação (com agregação `SUM` no grão `orgao + mês`, ver Seção 9.2 do `TERMO_HOMOLOGACAO_PRATA.md`) | ⏳ Pendente |
| 4.7 | Fato Capacitação ENAP (chave surrogate `sk_matricula`, medida `carga_horaria`) | ⏳ Pendente |
| 4.8 | Ponte Capacitação × Mês (factless, expande `dt_inicio`/`dt_fim` em uma linha por mês de duração do curso) | ⏳ Pendente |
| 4.9 | Decisão FinOps (External Tables vs. tabelas nativas) e configuração de particionamento/clustering nos 8 marts | ⏳ Pendente |
| 4.10 | Testes dbt nos marts da Gold e emissão do Termo de Homologação Ouro | ⏳ Pendente |

**Dependência:** Fase 3 concluída (✅, 07/08/2026).

**Bloqueios ativos:** Nenhum.

**Achados da Sprint 4.1, relevantes para as próximas sprints:** múltiplas suposições de estabilidade se mostraram falsas ao testar com população completa (nome de servidor pode mudar por casamento/retificação; nome/sigla de órgão DEPRO muda por reforma administrativa; `raca` em ENAP é resposta declarada por matrícula, não atributo fixo). Princípio reforçado para as sprints 4.2 em diante: nenhuma coluna descritiva deve ser tratada como estável em fato ou dimensão sem teste empírico prévio.
**Achados da Sprint 4.2, relevantes para as próximas sprints:** confirmada cobertura de 100% entre `stg_siape__remuneracao` e `stg_siape__ativos` na tríade `id_servidor_portal + year + month` (68.693.256 combinações, 0 órfãos) — decisão que permite enriquecimento via `LEFT JOIN` sem perda de linhas. Identificada e tratada a concomitência de vínculo (273.249 servidores, 26,8M linhas em `stg_siape__ativos`, fora do sentinela `-11`): quando um servidor tem mais de um vínculo ativo no mesmo mês, `cod_org_lotacao`/`cod_tipo_vinculo` ficam `NULL` em `fct_remuneracao`, preservando o fenômeno de mobilidade institucional que os Estudos 3 (Editais 02 e 04) investigam, em vez de atribuir um órgão arbitrário. Essa mesma concomitência é a origem estrutural do ADR-017, que a Sprint 4.3 vai formalizar como grão do Fato Vínculo/Ativos.
**Achados da Sprint 4.3, relevantes para as próximas sprints:** o ADR-017 original (6 colunas, Sprint 3.5) estava desatualizado, o schema real de `stg_siape__ativos` na Fase 4 é mais rico (43 colunas, incluindo blocos de cargo, função comissionada e exercício não mapeados em detalhe na Sprint 3.5). Validação incremental em população completa (nunca por amostra) revelou que `sk_vinculo` precisa de **8 colunas**, não 6: `id_servidor_portal, year, month, cod_org_lotacao, cod_tipo_vinculo, matricula, situacao_vinculo, cod_uorg_exercicio`. Processo de descoberta: 6 colunas → 242.588 grupos duplicados; +`matricula` → 324; +`situacao_vinculo` → 9 residuais (investigados individualmente, não descartados por amostra); +`cod_uorg_exercicio` → 0 grupos duplicados, confirmado em população completa. **Implicação analítica crítica para os Estudos B e C:** como `situacao_vinculo` e `cod_uorg_exercicio` compõem a chave, `sk_vinculo` muda quando a pessoa muda de situação/exercício, não é identificador estável de pessoa ao longo do tempo (só `id_servidor_portal` cumpre esse papel, exceto no subconjunto `-11`). Isso é intencional e útil para o Estudo 3 (mobilidade), mas é uma armadilha para quem for construir o Estudo 1 (trajetória/coorte) sem saber disso. `fct_vinculo_ativos` materializado com 96.563.830 linhas, validado como 100% da população de origem (excluído `-11`). Padrão de teste `relationships` composto (via coluna derivada `ano_mes` em `dim_tempo`) estabelecido como solução para FKs de chave composta, reaproveitável em qualquer fato futuro que precise validar integridade contra `dim_tempo`.
**Achados da Sprint 4.4, relevantes para as próximas sprints:** confirmado que nenhuma composição de chave é transferível entre fontes sem revalidação, mesmo quando o fenômeno (vínculos concomitantes) é o mesmo `stg_siape__aposentados` não possui `cod_uorg_exercicio`, tornando a chave de 8 colunas de Ativos inaplicável. Além disso, a coluna dominante na resolução do resíduo se inverteu entre as duas fontes: `situacao_vinculo` era dominante em Ativos (-97,2% do resíduo), enquanto `cod_tipo_vinculo` foi dominante em Aposentados (-87,4%), reforça que nenhuma coluna deve ser presumida "forte" só por analogia com um fato anterior. `fct_situacao_vinculo` materializado, 76.314.587 linhas, 13/13 testes dbt aprovados.

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
 
Ações imediatas desbloqueadas hoje (08/08/2026):
 
1. **Sprint 4.2**, construir o Fato Remuneração (`models/marts/fatos/fato_remuneracao.sql`), primeiro fato da Fase 4, grão simples sem chave surrogate.
2. **Verificação residual pendente** — confirmar via `INFORMATION_SCHEMA.COLUMNS` se a coluna `nome` está presente em `stg_siape__aposentados` e `stg_siape__afastamentos` (os dois modelos SIAPE ainda não checados). Os 3 modelos DEPRO e o modelo ENAP já têm schema confirmado sem coluna de nome de pessoa (DEPRO não tem; ENAP só tem `nome_curso`/`nome_turma`) — não precisam de nova verificação.
3. **Sprint 1.9** — retomar levantamento das bases Observatório de Pessoal, PEP e avaliar disponibilidade da ACT Lemann (não bloqueante, pode correr em paralelo à Fase 4).
4. **Sessão de Documentação Reversa (Produto 1)** — permanece planejada para o final da Camada Gold (Fase 4), conforme Seção 5.

---

## 5. Pendências Estratégicas de Longo Prazo

| Pendência | Contexto |
|:----------|:---------|
| Produto 1 — Edital 01 | Relatório de diagnóstico das bases não foi formalmente finalizado. Sessão de Documentação Reversa planejada ao final da Camada Gold (Fase 4). |
| Disponibilidade ACT Lemann | Acesso à base não confirmado. |
| Record Linkage ENAP | Confirmado em 02/08/2026 (ADR-009): `codigo_pessoa` é ID proprietário da EV.G, sem relação com CPF. ENAP não participa do JOIN nível-servidor com SIAPE/DEPRO. Estudos de capacitação (Trilhas B/C) ficam limitados a análises agregadas, salvo decisão futura por linkage probabilístico com validação de precisão. |
| Tabela de-para SIAPE↔SIORG | Confirmado em 07/08/2026 (Sprint 3.5): `cod_org_lotacao` (SIAPE) e `orgao_codigo_siorg` (DEPRO) são taxonomias de órgão incompatíveis, sem tabela de-para nas fontes atuais. Não bloqueia os estudos mapeados nos 4 editais atualmente, mas reaparece se o Estudo 2 (Trilha B) evoluir para cruzamento de custo por órgão entre SIAPE e projeções DEPRO. |


---

## 6. Gestão de Riscos Técnicos e Mitigações

| Risco Técnico | Impacto | Mitigação Implementada |
|:--- |:--- |:--- |
| **Bloqueio por Rate Limit (Erro 403)** | Alto | Pausas estruturadas e headers simulando navegadores reais. |
| **Inconsistência de schemas (Colunas)** | Médio | Filtro `Regex (Whitelist)` e isolamento da camada Bronze Normalized. |
| **Estouro de Memória (OOM)** | Alto | Motor vetorizado Polars, processamento colunar in-memory sem carregar o arquivo inteiro na RAM. |
| **Instabilidade de APIs e Firewalls (Timeouts, Erros 5xx)** | Alto | Blocos `try...except` e Graceful Degradation no motor de ingestão próprio. |
| **Duplicidade de registros** | Médio | Chave composta/surrogate por fonte (ver ADR-017 e `MODELO_DIMENSIONAL_GOLD.md`), `dbt tests`, e correções pontuais (`DISTINCT` em Afastamentos, `SUM` em Alocação DEPRO). |
| **Custo excessivo de processamento** | Alto | `Hive Partitioning` no Data Lake e `Clustering` no BigQuery (FinOps). |
| **Mudança de schema na origem (Contract Drift)** | Médio | Detecção planejada para Fase 2, validação de colunas a cada ingestão. |
| **Separador/encoding incorreto na origem (DEPRO)** | Alto | Descoberto em 02/08/2026 durante construção da Silver: os 3 CSVs do DEPRO usam `,` e `utf-8`, não `;`/`latin1` como documentado originalmente. Corrigido no código de ingestão (`depro.py`) e partições históricas reprocessadas via backfill Dagster. Risco geral para o projeto: parâmetros de ingestão documentados devem ser tratados como hipótese até validados contra o cabeçalho real do arquivo de origem, não como fato assumido. |
| **Inferência de tipo inconsistente entre partições (ENAP)** | Alto | Descoberto em 07/08/2026: `pl.scan_csv()` sem `schema_overrides` gerou schemas Parquet divergentes entre as 132 partições de `enap_capacitacao` (`idade`/`carga_horaria` como `INT64` em algumas, `STRING` em outras). Corrigido via reescrita pontual das partições e External Table recriada sem `autodetect`. Risco geral: qualquer ingestão futura via `pl.scan_csv()`/`pl.read_csv()` deve declarar `schema_overrides` explícito para colunas numéricas, para não repetir o problema. |

---

*Documento de estado do projeto — atualizar a cada sessão de trabalho.*  
*Para visão arquitetural e decisões técnicas, consulte `PROPOSTA_ARQUITETURA_MAPEAMENTO.md` e os ADRs em `docs/adr/`.*
---
