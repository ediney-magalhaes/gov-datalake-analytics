# Termo de Homologação Técnica (UAT) - Camada Prata (Staging)

**Projeto:** Data Lake - Plataforma de Análise de Pessoal da Administração Pública Federal

**Fase:** Camada Prata - Transformação e Padronização (dbt Core)

**Status:** Concluído. 8 modelos de staging construídos, testados e validados

**Última atualização:** 07/08/2026

---

## 1. Escopo da Homologação

Atesta-se a conclusão da Camada Prata (Staging), responsável pela transformação dos dados brutos da Camada Bronze (External Tables sobre Parquet no GCS) em estruturas padronizadas, tipadas e testadas, via dbt Core 1.12.0 com `dbt_utils` 1.3.0, sobre BigQuery.

Os oito modelos de staging, um por asset Bronze homologado, seguem padrão uniforme de construção: CTE `source` (leitura direta da External Table via `{{ source() }}`), seguida de CTE `final` (`dbt_utils.star()` com exclusão explícita das colunas que exigem tratamento, seguidas de conversão de tipo/data via `SAFE_CAST`/`SAFE.PARSE_DATE`/`SAFE.PARSE_DATETIME`).

| Modelo (Prata) | Fonte (Bronze) | Sistema |
|:---|:---|:---|
| `stg_siape__ativos` | `bronze.siape_ativos` | SIAPE |
| `stg_siape__remuneracao` | `bronze.siape_remuneracao` | SIAPE |
| `stg_siape__aposentados` | `bronze.siape_aposentados` | SIAPE |
| `stg_siape__afastamentos` | `bronze.siape_afastamentos` | SIAPE |
| `stg_depro__cargos` | `bronze.depro_cargos` | DEPRO |
| `stg_depro__aposentadorias` | `bronze.depro_aposentadorias` | DEPRO |
| `stg_depro__alocacao` | `bronze.depro_alocacao` | DEPRO |
| `stg_enap__capacitacao` | `bronze.enap_capacitacao` | ENAP |

---

## 2. Regras de Engenharia Aplicadas

- **Padronização estrutural:** `dbt_utils.star(from=source(...), except=[...])`, seleção explícita por exclusão, preservando fidelidade ao schema da fonte, com tratamento pontual apenas das colunas que exigem conversão.
- **Tipagem estrita:** conversão de datas via `SAFE.PARSE_DATE`/`SAFE.PARSE_DATETIME` (formatos `%d/%m/%Y` e `%Y-%m-%d %H:%M:%S`, conforme a fonte); conversão numérica via `SAFE_CAST`; valores monetários em formato brasileiro (vírgula decimal) tratados pelo macro `converte_valor_brl.sql` (`SAFE_CAST(REPLACE(coluna, ',', '.') AS FLOAT64)`).
- **Tratamento de `nome`:** a coluna `nome` está presente em `stg_siape__ativos` e `stg_siape__remuneracao` (confirmado via `INFORMATION_SCHEMA.COLUMNS`, 07/08/2026), sem exclusão sistemática. Isso não representa risco de conformidade: nome de servidor público no exercício da função é dado de transparência ativa, com respaldo na Lei de Acesso à Informação, diferente de CPF (que é pseudonimizado desde a Bronze, conforme ADR-013). Não existe hoje uma convenção formal e uniforme sobre inclusão/exclusão de `nome` entre os 8 modelos; essa uniformidade, se desejada, é uma decisão de padronização pendente, não um requisito de LGPD.
- **Fidelidade sobre correção prematura:** nenhuma imputação de valores nulos é aplicada na Prata (rejeitando explicitamente a prática de substituição por texto padrão tipo "NAO INFORMADO", presente em rascunho anterior deste documento e nunca implementada). Nulos permanecem nulos, tratados na camada e no momento analítico apropriado.

---

## 3. Suíte de Testes dbt (Sprint 3.4)

Testes aplicados aos 8 modelos, mapeados individualmente contra as colunas relevantes aos estudos propostos, não por convenção genérica de mercado.

**Tipos de teste efetivamente presentes no repositório (verificado via `Select-String` sobre os arquivos `_models.yml`, 07/08/2026):**
- `not_null`: 32 ocorrências
- `dbt_utils.accepted_range`: 16 ocorrências
- **Total: 48 testes**

**Resultado da execução:** 48/48 `PASS`.

`dbt_utils.unique_combination_of_columns` foi tentado durante a sessão sobre `stg_siape__ativos`, mas não permanece em nenhum model final: o teste falhou (13.348.412 violações) e a causa investigada (vínculos concomitantes legítimos) levou à decisão formal de não aplicá-lo na Prata (ADR-017, Seção 5).

---

## 4. Achados e Correções Técnicas Aplicadas na Prata

Descobertas de qualidade de dado feitas durante as Sprints 3.4/3.5, com correção aplicada diretamente nos modelos de staging (não deferidas para a Gold):

| Achado | Modelo afetado | Correção aplicada |
|:---|:---|:---|
| Linha de rodapé do CSV contaminando a última partição | `stg_siape__remuneracao` | `WHERE id_servidor_portal IS NOT NULL AND id_servidor_portal != ''` |
| Separador (`;` para `,`) e encoding (`latin1` para `utf-8`) incorretos na ingestão | `stg_depro__alocacao`, `stg_depro__cargos`, `stg_depro__aposentadorias` | Correção no asset Dagster (`depro.py`) e reprocessamento de 95 partições Bronze |
| Duplicação exata de linha (mesmo `ingestion_timestamp`, todas as colunas idênticas), 228.704 grupos, 229.159 linhas excedentes (aproximadamente 2,46% da tabela) | `stg_siape__afastamentos` | `select distinct * from final` |
| Inconsistência de tipo `idade`/`carga_horaria` (`INT64` vs `STRING`) entre as 132 partições Bronze, causada por inferência de schema sem `schema_overrides` na ingestão | `stg_enap__capacitacao` | Reescrita das 132 partições Parquet (script pontual) e External Table recriada sem `autodetect`, com `SAFE_CAST` já presente no model |

---

## 5. Limitações Estruturais Documentadas (não corrigidas na Prata, decisão formal)

Achados que **não** representam erro de dado, mas características legítimas ou limitações das fontes, com tratamento explicitamente deferido para a Camada Ouro:

- **ADR-017, ausência de teste de unicidade em `stg_siape__ativos` e `stg_siape__aposentados`:** `id_servidor_portal + year + month` não é grão único nessas fontes; um mesmo servidor pode ter múltiplos vínculos concomitantes legítimos (cargo e função, múltiplas matrículas, múltiplos órgãos). Resolução de grão via chave surrogate técnica (`sk_vinculo`) deferida para os models de Mart na Fase 4, conforme `docs/MODELO_DIMENSIONAL_GOLD.md`.
- **Valor sentinela `id_servidor_portal = '-11'`:** confirmado como fenômeno transversal a toda a base SIAPE (4.096.137 linhas em Ativos, 1.746.006 em Aposentados), representando servidores sob sigilo legal, não erro de ingestão, mas limitação de identificação individual da fonte pública. `id_servidor_portal` não é identificador confiável de pessoa para esse subconjunto.
- **Escopo real de `stg_siape__aposentados`:** a fonte contém 45 categorias de `situacao_vinculo`, não apenas aposentadoria (`APOSENTADO` é 29.941.096 de mais de 80M de linhas), incluindo cessão, contratação temporária, celetistas e outras situações de vínculo. Reaproveitada como Fato genérico "Situação de Vínculo" na Gold.
- **173 registros residuais em `stg_siape__afastamentos`** com `data_inicio_afastamento` e `data_fim_afastamento` ambas nulas (0,002% da tabela), não representam afastamento válido; exclusão deferida para a construção da Mart.
- **Taxa de não resposta de aproximadamente 26% na coluna `raca`** em `stg_enap__capacitacao` (5,1M de 19,3M registros), aparenta ser campo opcional no formulário de matrícula (existe resposta ativa "Não quero informar" distinta de nulo); a considerar na metodologia do Estudo 7 (Diversidade Interseccional).
- **Colisão de chave natural `cod_matricula`** em `stg_enap__capacitacao`: 172 colisões confirmadas em 19.346.163 linhas (hash truncado sem garantia de unicidade global), resolvida via chave surrogate composta na Camada Ouro, não na Prata.

---

## 6. Conformidade Legal e Segurança (LGPD)

Mantida a pseudonimização já validada na Camada Bronze (ADR-013, SHA-256 mais Salt) sobre a coluna de CPF. A coluna `nome` permanece presente em `stg_siape__ativos` e `stg_siape__remuneracao` (ver Seção 2); tratando-se de dado de transparência ativa de servidor público, isso não constitui violação de LGPD. Nenhum dado sensível (CPF em texto claro) é exposto além do já tratado na ingestão.

---

## 7. Evidências de Validação

- **Ambiente:** BigQuery, dataset `prata`, projeto `gov-datalake-analytics`
- **Ferramenta:** dbt Core 1.12.0, adapter `dbt-bigquery`, `dbt_utils` 1.3.0
- **Validação de cada modelo:** `dbt compile`, seguido de `dbt run`, consulta direta no BigQuery, revisão de diff e commit
- **Repositório:** branch `main`, pós merge de `feature/models-staging` (Sprint 3.3) e `test/dbt-staging-siape-depro-enap` (Sprint 3.4)
- **ADRs relacionadas:** ADR-009 (chave universal `id_servidor_portal`), ADR-017 (não aplicação de teste de unicidade em `stg_siape__ativos`)
- **Documento sucessor:** `docs/MODELO_DIMENSIONAL_GOLD.md`, insumo direto para a construção física da Camada Ouro (Fase 4)

---

## 8. Assinaturas de Validação

- **Arquiteto/Engenheiro de Dados:** Ediney Magalhães Junior
- **Validação Técnica:** Evidência registrada via execução da suíte de 48 testes dbt e inspeção direta de dados no BigQuery (população completa, não amostragem)
- **Status Final:** Homologação completa. 8 modelos de staging construídos, testados e com achados de qualidade formalmente documentados (corrigidos ou deferidos com justificativa), aptos a servir de fonte para a construção da Camada Ouro

---

## 9. Riscos Conhecidos e Limitações Operacionais

### 9.1 Ausência de tabela de-para entre codificações de órgão
`stg_siape__*` usa `cod_org_lotacao` (código legado/interno do SIAPE); `stg_depro__*` usa `orgao_codigo_siorg` (código SIORG oficial). Confirmado apenas 1 código em comum entre 381 valores distintos (SIAPE) e 198 (DEPRO): taxonomias incompatíveis, sem tabela de-para disponível nas fontes atuais. Não bloqueia os estudos mapeados nos 4 editais (nenhum exige cruzamento órgão a órgão entre as duas fontes); registrado como limitação, não como pendência ativa.

### 9.2 Grão de `stg_depro__alocacao` inconsistente com o dicionário oficial da fonte
Dicionário de dados da SEGES/Raio-X declara grão único por `orgao_codigo_siorg + ano_mes_referencia`, mas 385 grupos de linhas paralelas com medidas divergentes foram encontrados na população real. Causa raiz não determinável a partir da documentação disponível. Tratamento (agregação `SUM`) aplicado na Camada Ouro, não na Prata; a Prata preserva a fonte fiel, incluindo essa anomalia.