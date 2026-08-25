# Modelo Dimensional — Camada Ouro (Gold)

**Projeto:** Data Lake Analytics — Gestão de Pessoal (PNUD BRA/21/011 — MGI/SETE/SGP)
**Sprint de origem:** 3.5 — Modelagem Dimensional Kimball
**Status:** 8 fatos e 7 dimensões fechados (07/08/2026) — Fase 4 em andamento (7 dimensões e 1 fato concluídas)

---

## 1. Propósito deste documento

Este documento registra as decisões de modelagem dimensional (Kimball) para a Camada Ouro, tomadas durante a Sprint 3.5. Cada Fato e Dimensão é documentado com:

- **Grão**: a granularidade exata de uma linha do fato — o que ela representa de forma única
- **Dimensões**: as chaves de contexto (quem, onde, quando) que descrevem o evento
- **Medidas**: os valores numéricos que se somam/agregam
- **Decisões e exclusões**: escolhas de modelagem e o motivo, incluindo colunas deliberadamente excluídas

Este documento é o insumo direto para:
- A construção dos `models/marts/*.sql` na Fase 4
- A reescrita do Termo de Homologação da Camada Prata (atualmente desatualizado em relação aos achados reais das Sprints 3.4/3.5)
- A sessão de Documentação Reversa do Produto 1 (Edital 01)

> **Nota:** as tabelas de staging (Prata) que alimentam os fatos abaixo foram testadas na Sprint 3.4, com achados relevantes registrados em `docs/adrs/0017-nao-aplicacao-teste-unicidade-stg_siape__ativos.md` e no `ROADMAP_ARQUITETURAL.md` (seção Sprint 3.5). Este documento pressupõe esses achados como contexto.

---

## 2. Fatos

### 2.1 Fato Remuneração

**Fonte (Prata):** `stg_siape__remuneracao`

**Grão:** um registro por `id_servidor_portal` + `year` + `month` — um evento de pagamento por servidor por mês de competência.

> Confirmado empiricamente na Sprint 3.5 (06/08/2026): diferente de `stg_siape__ativos` (ver ADR-017), a combinação `id_servidor_portal + year + month` já é única em Remuneração — não há duplicidade por vínculos concomitantes nesta fonte. Verificado via `GROUP BY ... HAVING COUNT(*) > 1` sobre a população completa, sem resultados.

**Dimensões:**
- `id_servidor_portal` → `dim_servidor`
- `year` / `month` → `dim_tempo`
- `cod_org_lotacao` → `dim_orgao_siape` (obtido por enriquecimento — ver achado abaixo)
- `cod_tipo_vinculo` → `dim_tipo_vinculo` (obtido por enriquecimento — ver achado abaixo)

**Enriquecimento via Fato Vínculo/Ativos (Sprint 4.2, 17/08/2026):**
`stg_siape__remuneracao` não carrega `cod_org_lotacao` nem `cod_tipo_vinculo` — a fonte de Remuneração publica apenas valores monetários, sem contexto organizacional. Verificado empiricamente, população completa: 100% das 68.693.256 combinações `(id_servidor_portal, year, month)` de Remuneração têm correspondência em `stg_siape__ativos` (0 casos órfãos). Por essa cobertura total, `fct_remuneracao` busca `cod_org_lotacao`/`cod_tipo_vinculo` via `LEFT JOIN` contra `stg_siape__ativos`, pela mesma tríade de chave.

**Achado — concomitância de vínculo propagada ao Fato Remuneração (Sprint 4.2, 17/08/2026):**
O enriquecimento acima herda o fenômeno de vínculos concomitantes já documentado no ADR-017 e na seção 2.2. Verificado empiricamente, população completa: **273.249 servidores distintos** possuem mais de um vínculo ativo no mesmo `(year, month)`, totalizando **26.781.976 linhas envolvidas** em `stg_siape__ativos` (excluído o sentinela `-11`, tratado à parte).

Como a fonte de Remuneração não distingue qual vínculo concomitante gerou o pagamento, atribuir um órgão/tipo de vínculo único de forma arbitrária corromperia justamente o fenômeno que o Estudo 3 da Trilha B (Fluxos e Fronteiras — Mobilidade Funcional e Institucional, Edital 02) e o Estudo 3 da Trilha C (Diversidade e Desigualdades, Edital 04) se propõem a investigar.

**Decisão:** quando um servidor possui mais de um vínculo no mesmo mês, `cod_org_lotacao` e `cod_tipo_vinculo` são gravados como `NULL` em `fct_remuneracao` para aquele registro, as medidas de remuneração permanecem intactas e íntegras, apenas o contexto organizacional fica marcado como não atribuível. Mesmo princípio de tratamento já aplicado ao sentinela `-11`: a ambiguidade é um dado real da fonte, não um erro a mascarar.

**Medidas:** todas as colunas com sufixo `_reais` da fonte, entre elas:
- `remuneracao_basica_bruta_reais`
- `gratificacao_natalina_reais`
- `ferias_reais`
- `outras_remuneracoes_eventuais_reais`
- `irrf_reais`
- `pssrpgs_reais`
- `demais_deducoes_reais`
- `pensao_militar_reais`
- `fundo_saude_reais`
- `taxa_ocupacao_imovel_funcional_reais`
- `remuneracao_deducoes_obrigatorias_reais`
- `verbas_indenizatorias_pessoal_civil_reais`
- `verbas_indenizatorias_pessoal_militar_reais`
- `verbas_indenizatorias_desligamento_voluntario_reais`
- `total_verbas_indenizatorias_reais`

**Decisões e exclusões:**
- Todas as colunas com sufixo `_dolar` são **excluídas** do modelo Gold. Os 8 estudos dos editais tratam de política pública brasileira, financiada e reportada em Reais — a versão em dólar não tem uso analítico no escopo do projeto. As colunas permanecem na Prata (fiel à fonte bruta), mas não são carregadas no Fato.
- A relação matemática exata entre `remuneracao_basica_bruta_reais` e as demais colunas (deduções, verbas) não foi reconstruída por fórmula — cada componente é tratado como medida independente do mesmo evento, sem necessidade de recalcular soma/total na Prata ou no Fato.

---

### 2.2 Fato Vínculo/Ativos

**Fonte (Prata):** `stg_siape__ativos`

**Grão:** um registro por **vínculo** de servidor por mês — não por servidor. Um mesmo `id_servidor_portal` pode legitimamente gerar múltiplas linhas no mesmo `year`/`month` quando o servidor possui mais de um vínculo simultâneo (ver ADR-017: cargo + função, múltiplas matrículas, múltiplos órgãos).

**Resolução do ADR-017 — atualizada (Sprint 4.3, 17/08/2026):** a composição original de 6 colunas (Sprint 3.5) foi revalidada com o schema real de `stg_siape__ativos`, que na Fase 4 se mostrou mais rico do que o disponível na Sprint 3.5 (43 colunas, incluindo blocos de cargo, função comissionada e exercício antes não mapeados em detalhe). Teste empírico em população completa mostrou que as 6 colunas originais não fechavam o grão: restavam 242.588 grupos duplicados. Investigação incremental, sempre validada em população completa (nunca por amostra), identificou duas colunas adicionais necessárias — `matricula` e `situacao_vinculo` — reduzindo o resíduo em etapas (242.588 → 324 → 9 grupos).

`sk_vinculo` passa a ser gerada por **8 colunas**, superando o ADR-017 original:

```sql
{{ dbt_utils.generate_surrogate_key(['id_servidor_portal', 'year', 'month', 'cod_org_lotacao', 'cod_tipo_vinculo', 'matricula', 'situacao_vinculo', 'cod_uorg_exercicio']) }} as sk_vinculo
```

Verificado empiricamente (17/08/2026), população completa: **0 grupos duplicados** nesse grão de 8 colunas.

**Resíduo residual aceito:** dos 324 grupos que restavam após 7 colunas, `situacao_vinculo` isolada resolvia 315 (97,2%). Os 9 grupos remanescentes (≈20-27 linhas, envolvendo servidores com múltiplos registros de `cod_uorg_exercicio` no mesmo mês — ex.: cessão/exercício em mais de um órgão simultaneamente) foram investigados individualmente (não por amostra genérica) e resolvidos com a 8ª coluna, `cod_uorg_exercicio`. Proporção do resíduo antes da 8ª coluna: 9 grupos em ~13,3M combinações possíveis (<0,0001%) — mesmo padrão de tratamento de ruído desprezível de fonte já aplicado ao sentinela `-11`.

**Implicação analítica — `sk_vinculo` não é identificador estável de pessoa ao longo do tempo:** como `situacao_vinculo` e `cod_uorg_exercicio` compõem a chave, uma mudança em qualquer um desses atributos (ex.: servidor que passa de "ATIVO PERMANENTE" para "CEDIDO", ou muda de UORG de exercício) gera uma **nova** `sk_vinculo` para a mesma pessoa/cargo. Isso é o comportamento correto para os Estudos de mobilidade (Estudo 3, Trilha B/C a mudança em si é o evento de interesse), mas significa que análises de trajetória/coorte (Estudo 1, Trilha B) não podem usar `sk_vinculo` como chave de rastreamento de indivíduo ao longo do tempo apenas `id_servidor_portal` cumpre esse papel (exceto no subconjunto sob sentinela `-11`, onde nem `id_servidor_portal` identifica indivíduo).

**Construção física (Sprint 4.3, 17/08/2026):** `fct_vinculo_ativos` materializado com 96.563.830 linhas, validado como equivalente a 100% de `SELECT COUNT(*) FROM stg_siape__ativos WHERE id_servidor_portal != '-11'`, confirmando que a geração de `sk_vinculo` não duplicou nem perdeu linhas da origem. Coluna derivada `ano_mes` (`CONCAT(year, '-', LPAD(month, 2, '0'))`) adicionada ao fato especificamente para permitir teste `relationships` composto contra `dim_tempo.ano_mes` — testes `relationships` isolados sobre `year` e `month` separadamente foram descartados por não validarem a combinação real (mesmo problema estrutural que motivou a chave composta do próprio `sk_vinculo`). 11/11 testes dbt aprovados.

`sk_vinculo` passa a ser a chave primária técnica do fato. O teste de unicidade (`unique`/`not_null`) deve ser aplicado sobre `sk_vinculo`, não sobre `id_servidor_portal` isoladamente. Qualquer resíduo de duplicidade restante após a chave surrogate deve ser investigado como caso novo, não presumido resolvido.

**Dimensões:**
- `id_servidor_portal` → `dim_servidor`
- `year` / `month` → `dim_tempo`
- `cod_org_lotacao` → `dim_orgao_siape`
- `cod_tipo_vinculo` / `tipo_vinculo` → `dim_tipo_vinculo`

**Achado — valor sentinela em `id_servidor_portal` (Sprint 3.5, 06/08/2026):**
`id_servidor_portal = '-11'` ocorre em **4.096.137 linhas** de `stg_siape__ativos` (~5% da tabela). Não é erro de ingestão: todas essas linhas têm `descricao_cargo = "Sigiloso"` e `situacao_vinculo = "Sigiloso"` — servidores sob sigilo legal (cargos de segurança institucional), cuja identificação real o Portal da Transparência não publica. `-11` é um placeholder da fonte, não um identificador de pessoa.

> **Atualização (07/08/2026):** confirmado que este é um fenômeno **transversal a toda a base SIAPE**, não específico de Ativos — ver achado idêntico em `stg_siape__aposentados` (seção 2.3). O mesmo tratamento de `dim_servidor` (ver seção 3.1) se aplica a qualquer fato construído sobre `id_servidor_portal`.

Consequência: milhões de servidores diferentes compartilham a mesma chave falsa. Isso não quebra `sk_vinculo` (que usa outras colunas além de `id_servidor_portal`), mas invalida `id_servidor_portal` como identificador único de pessoa para todo esse subconjunto. Qualquer análise que dependa de contar/rastrear indivíduos (ex: Estudo 1 — trajetórias, Estudo 8 — liderança) precisa tratar `id_servidor_portal = '-11'` como "não identificável", nunca como uma única pessoa reaparecendo.

**Pendências de verificação (não bloqueantes para esta sprint):**
- Confirmar se o mesmo padrão de sigilo (`-11` ou equivalente) existe em `stg_siape__remuneracao` e `stg_siape__afastamentos` — **`stg_siape__aposentados` já confirmado (seção 2.3)**
- Avaliar se `dim_servidor` precisa de uma regra explícita para tratar registros sigilosos (ex: excluir de contagens de indivíduos únicos, ou marcar com flag `is_sigiloso`)

---

### 2.3 Fato Situação de Vínculo

**Fonte (Prata):** `stg_siape__aposentados`

**Natureza do fato:** apesar do nome herdado da fonte, esta tabela não representa um evento exclusivo de aposentadoria, é um **retrato mensal da situação de vínculo** de cada registro, do qual `APOSENTADO` (29.941.096 linhas) é apenas uma das 45 categorias possíveis de `situacao_vinculo` (outras incluem `ATIVO PERMANENTE`, `CEDIDO/REQUISITADO`, `CONTRATO TEMPORARIO`, `CELETISTA/EMPREGADO`, `Sigiloso`, entre outras). Por isso, adota-se **um único Fato genérico**, reutilizável pelos Estudos 3 (Fluxos e Fronteiras) e 4 (Contratações Temporárias) via filtro em `situacao_vinculo`, em vez de fatos separados por categoria — decisão alinhada ao princípio de que fatos separados exigiriam uma classificação de negócio não pedida pelos editais.

**Tipo de fato: Factless (sem medida numérica aditiva).** Verificado no schema: as colunas exclusivas desta fonte em relação a Ativos (`cod_tipo_aposentadoria`, `tipo_aposentadoria`, `data_aposentadoria`) são categóricas/data, não numéricas. Não há valor de proventos, tempo de contribuição ou qualquer grandeza somável na fonte. O grão é a **ocorrência** do vínculo naquela situação, não uma quantidade.

**Grão — revalidado (Sprint 4.4, 21/08/2026):** a composição provisória da Sprint 3.5 (6 colunas, resíduo de 13.088 grupos nunca investigado caso a caso) foi descartada e revalidada do zero contra o schema real de `stg_siape__aposentados` na Fase 4. Achado estrutural relevante: esta fonte **não possui** a coluna `cod_uorg_exercicio` que fechou o grão de Ativos (seção 2.2), o schema de Aposentados só tem a família "lotação" (`cod_uorg_lotacao`, `cod_org_lotacao`, `cod_orgsup_lotacao`), sem conceito de "exercício". Isso é coerente com a natureza do dado: exercício representa onde o servidor trabalha ativamente no dia a dia, conceito que não se aplica a quem já está aposentado. Consequência prática: a chave de 8 colunas do ADR-017 não pôde ser reaproveitada — a construção da chave desta sprint partiu do zero, reaproveitando apenas o *processo* empírico incremental (nunca a composição de colunas).

Verificado empiricamente (21/08/2026), população completa (`GROUP BY` + `HAVING COUNT(*) > 1`), excluindo o sentinela `-11`:
- Grão simples (`id_servidor_portal + year + month`): **6.971.333 grupos duplicados**.
- Teste incremental de colunas candidatas, isoladas contra o baseline: `cod_tipo_vinculo` (-87,4%, dominante — diferente de Ativos, onde `situacao_vinculo` foi a coluna dominante), `situacao_vinculo` (-14,7%), `matricula` (-11,6%), `cod_uorg_lotacao` (-10,7%), `data_aposentadoria` (-8,0%), `cod_org_lotacao` (-6,2%), `cod_tipo_aposentadoria` (-0,9%).
- Chave final combinada: **0 grupos duplicados** em população completa com 7 colunas.

`sk_situacao_vinculo` é gerada por **7 colunas** (nome escolhido deliberadamente diferente de `sk_vinculo`, para não colidir semanticamente com a chave de Ativos, que tem composição diferente):

```sql
{{ dbt_utils.generate_surrogate_key(['id_servidor_portal', 'year', 'month', 'cod_tipo_vinculo', 'situacao_vinculo', 'matricula', 'cod_org_lotacao']) }} as sk_situacao_vinculo
```

**Teste de necessidade da chave:** cada uma das 4 últimas colunas testadas (`cod_tipo_vinculo`, `situacao_vinculo`, `matricula`, `cod_org_lotacao`) foi confirmada como necessária — a remoção de `cod_org_lotacao` sozinha reabre resíduo de 327.092 grupos, confirmando que nenhuma das 7 colunas é redundante.

**Construção física (Sprint 4.4, 21/08/2026):** `fct_situacao_vinculo` materializado com 76.314.587 linhas, validado como equivalente a 100% de `SELECT COUNT(*) FROM stg_siape__aposentados WHERE id_servidor_portal != '-11'`. Coluna derivada `ano_mes` adicionada ao fato, mesmo padrão da seção 2.2, para viabilizar teste `relationships` composto contra `dim_tempo.ano_mes`. 13/13 testes dbt aprovados.

**Dimensões:**
- `id_servidor_portal` → `dim_servidor`
- `year` / `month` → `dim_tempo` (via `ano_mes`)
- `cod_org_lotacao` → `dim_orgao_siape`
- `cod_tipo_vinculo` → `dim_tipo_vinculo`

**Atributos degenerados** (viajam com o fato, sem dimensão própria, categóricos exclusivos desta fonte, sem tabela de apoio nem reutilização fora deste fato):
- `situacao_vinculo` (as 45 categorias, chave de filtro para os Estudos 3 e 4; também é coluna de grão, não apenas atributo)
- `matricula` (coluna de grão)
- `cod_tipo_aposentadoria` / `tipo_aposentadoria`
- `data_aposentadoria`
- `descricao_cargo`, `tipo_vinculo`, `regime_juridico`

**Achado — valor sentinela confirmado (Sprint 3.5, 07/08/2026, mantido):**
`id_servidor_portal = '-11'` ocorre em **1.746.006 linhas**, e o total coincide exatamente com a contagem de `situacao_vinculo = 'Sigiloso'` (1.746.006). Confirma que `-11` é o mesmo placeholder de sigilo legal já identificado em Ativos (seção 2.2), agora comprovado como fenômeno transversal da base SIAPE, não específico de uma fonte.

**Decisões e exclusões:**
- `nome` (presente no bruto) é excluído, seguindo a mesma decisão de governança/LGPD já aplicada em Ativos.

---

### 2.4 Fato Afastamentos

**Fonte (Prata):** `stg_siape__afastamentos`

**Tipo de fato: Factless.** Schema enxuto (11 colunas): `id_servidor_portal`, `year`, `month`, `hash_cpf`, `data_inicio_afastamento`, `data_fim_afastamento` + metadados. Sem `cod_org_lotacao`, `cod_tipo_vinculo` nem `matricula`, não carrega órgão nem tipo de vínculo, portanto `dim_orgao_siape` e `dim_tipo_vinculo` não se aplicam a este fato.

**Grão:** `id_servidor_portal + year + month + data_inicio_afastamento + data_fim_afastamento`.

> **Bug de duplicação exata descoberto e corrigido (Sprint 3.5, 07/08/2026):** grão simples (`id_servidor_portal + year + month`) tinha 362.695 grupos duplicados. Grão estendido com as datas reduziu para 228.704, praticamente inalterado, indicando que a causa não era concomitância legítima. Investigação de exemplo real (5 linhas de um mesmo grupo) confirmou linhas **bit-a-bit idênticas**, inclusive `ingestion_timestamp`, duplicação exata de linha na Bronze/Silver, não fenômeno de negócio. Escala confirmada: 228.704 grupos duplicados exatos, 457.863 linhas envolvidas, 229.159 linhas excedentes (~2,46% da tabela).
>
> **Correção aplicada:** `select * from final` alterado para `select distinct * from final` em `stg_siape__afastamentos.sql` (commit `fix:` dedicado). Revalidado após `dbt run`: **0 grupos duplicados** no grão estendido.

**Revalidação na Fase 4 (Sprint 4.5, 24/08/2026):** o grão registrado na Sprint 3.5 foi reconfirmado empiricamente contra o schema atual, não presumido. Grão simples (`id_servidor_portal + year + month`): **158.678 grupos duplicados** (número menor que os 362.695 originais, coerente com o efeito do `DISTINCT` aplicado na Silver desde a correção). Grão estendido com as duas datas: **0 grupos duplicados** em população completa, confirma que a correção de 07/08/2026 continua efetiva e nenhuma coluna adicional é necessária.

Sentinela `id_servidor_portal = '-11'` revalidado: **0 ocorrências**, achado da Sprint 3.5 confirmado sem alteração. As 173 linhas com `data_inicio_afastamento` e `data_fim_afastamento` ambas nulas também revalidadas: contagem idêntica (173), decisão de exclusão mantida sem mudança.

**Decisão de chave — sem surrogate key:** diferente de Vínculo/Ativos e Situação de Vínculo (7-8 colunas, `sk_*`), `fct_afastamentos` usa exclusivamente a combinação de colunas naturais como grão, sem chave surrogate técnica. Critério aplicado: grão com 5 colunas naturais e legíveis não justifica o custo de uma `sk_*`, mesmo padrão já usado em `fct_remuneracao` (grão de 3 colunas). Surrogate key só se justifica quando o grão natural é extenso o suficiente para prejudicar legibilidade/uso em joins e testes (caso de Vínculo/Ativos e Situação de Vínculo).

**Construção física (Sprint 4.5, 24/08/2026):** `fct_afastamentos` materializado com 9.069.323 linhas, validado como equivalente a 100% de `SELECT COUNT(*) FROM stg_siape__afastamentos WHERE data_inicio_afastamento IS NOT NULL OR data_fim_afastamento IS NOT NULL`. Coluna derivada `ano_mes` adicionada, mesmo padrão dos fatos anteriores, para viabilizar teste `relationships` composto contra `dim_tempo.ano_mes`. `hash_cpf` excluído do fato, sem uso analítico direto nos estudos, já disponível via join com `dim_servidor` por `id_servidor_portal`. 5/5 testes dbt aprovados.

**Dimensões:**
- `id_servidor_portal` → `dim_servidor`
- `year` / `month` → `dim_tempo` (via `ano_mes`)

**Decisões e exclusões:**
- As 173 linhas com `data_inicio_afastamento` e `data_fim_afastamento` ambas nulas são excluídas na construção da Mart: `WHERE data_inicio_afastamento IS NOT NULL OR data_fim_afastamento IS NOT NULL`.
- Sentinela `id_servidor_portal = '-11'` **confirmado ausente** nesta fonte (0 ocorrências), coerente com a tabela não carregar `descricao_cargo`/`situacao_vinculo`.
- `hash_cpf` excluído do fato físico (redundante com `dim_servidor`, sem uso nos estudos).

---

### 2.5 Fato Cargos DEPRO

**Fonte (Prata):** `stg_depro__cargos`

**Tipo de fato: com medida (não factless).** Diferente das fontes SIAPE, DEPRO traz contagens agregadas por órgão — não há `id_servidor_portal`, é dado pré-agregado no nível de órgão, mesmo padrão já estabelecido para o PEP (fato independente, sem join individual).

**Grão:** `orgao_codigo_siorg + carreira + grupo_cargo + cargo + year + month`.

> Verificado empiricamente (07/08/2026): 0 grupos duplicados nesse grão, população completa.

**Medida:** `quantidade`

**Dimensões:**
- `orgao_codigo_siorg` → `dim_orgao_depro`
- `year` / `month` → `dim_tempo`

**Atributos degenerados:** `carreira`, `grupo_cargo`, `cargo`

---

### 2.6 Fato Aposentadorias Previstas DEPRO

**Fonte (Prata):** `stg_depro__aposentadorias`

**Tipo de fato: com medida.**

**Grão:** `orgao_codigo_siorg + faixa_etaria + natureza_juridica + escolaridade_cargo + plano_carreira + grupo_cargo + cargo + sexo + year + month + ano_aposentadoria`.

> Decisão arquitetural (07/08/2026): a tabela tem duas dimensões temporais distintas — `year`/`month` (quando a projeção foi apurada) e `ano_aposentadoria` (horizonte da projeção). Mantidas as duas no grão: descartar `year`/`month` perderia a capacidade de analisar revisão da estimativa ao longo do tempo (relevante para o Estudo 2 — simulação de cenários); descartar `ano_aposentadoria` destruiria o propósito da tabela. Verificado empiricamente: 0 grupos duplicados nesse grão, população completa.

**Medida:** `quantidade_prevista`

**Dimensões:**
- `orgao_codigo_siorg` → `dim_orgao_depro`
- `year` / `month` → `dim_tempo` (apuração)

**Atributos degenerados:** `faixa_etaria`, `natureza_juridica`, `escolaridade_cargo`, `plano_carreira`, `grupo_cargo`, `cargo`, `sexo`, `ano_aposentadoria` (horizonte de projeção)

---

### 2.7 Fato Alocação DEPRO

**Fonte (Prata):** `stg_depro__alocacao`

**Tipo de fato: com medida, com pré-agregação obrigatória.**

**Grão:** `orgao_codigo_siorg + year + month`.

> **Anomalia descoberta e corrigida (Sprint 3.5, 07/08/2026):** 385 grupos com linhas paralelas para o mesmo órgão/mês, com **medidas diferentes** entre si (não duplicação de linha — os campos descritivos são idênticos, mas `quantidade_servidores_*` variam). O dicionário de dados oficial da fonte (SEGES/Raio-X, `repositorio.dados.gov.br/seges/raio-x/dicionario-de-dados.odt`) confirma que a tabela `alocacao-servidores.csv` **não tem nenhuma dimensão adicional** além de órgão e `ano_mes_referencia` — ou seja, essas linhas paralelas **violam o grão que a própria fonte declara ter**. Causa raiz não determinável a partir da documentação disponível (mesmo `ingestion_timestamp` nas linhas paralelas, descartando hipótese de reprocessamento em datas diferentes).
>
> **Correção aplicada:** agregação via `SUM` das 5 medidas no grão `orgao_codigo_siorg + year + month`, absorvendo as linhas paralelas. Total bruto pré-agregação de `quantidade_servidores_quadro_pessoal`: 28.012.958 — validado como base de comparação para conferir que a soma não distorce o total geral após a agregação no model físico (Fase 4).

**Medidas:** `quantidade_servidores_cedidos_apf`, `quantidade_servidores_cedidos_outros`, `quantidade_servidores_cedidos`, `quantidade_servidores_quadro_pessoal`, `quantidade_estagiarios`

**Dimensões:**
- `orgao_codigo_siorg` → `dim_orgao_depro`
- `year` / `month` → `dim_tempo`

---

### 2.8 Fato Capacitação ENAP

**Fonte (Prata):** `stg_enap__capacitacao`

**Tipo de fato: com medida (transacional).** Diferente das demais fontes SIAPE, tem medida numérica real: `carga_horaria` (horas de treinamento).

**Grão:** `sk_matricula`, chave surrogate técnica:
```sql
{{ dbt_utils.generate_surrogate_key(['cod_matricula', 'codigo_pessoa', 'cod_turma', 'dt_matricula']) }} as sk_matricula
```

> **Achado — colisão de chave natural (Sprint 3.5, 07/08/2026):** `cod_matricula` sozinho tinha 172 colisões em 19.346.163 linhas (total ≠ distintos). Investigação de exemplo real confirmou que são matrículas genuinamente diferentes (cursos, pessoas, datas distintas) compartilhando o mesmo `cod_matricula` — hash truncado (10 caracteres hex) sem garantia de unicidade global em base de 19M+ linhas (paradoxo do aniversário). Resolvido via chave composta `cod_matricula + codigo_pessoa + cod_turma + dt_matricula` — verificado empiricamente: 0 grupos duplicados após a composição.

**Medida:** `carga_horaria`

**Dimensões:**
- `codigo_pessoa` → `dim_pessoa_enap` (independente de `dim_servidor` — ver nota abaixo)
- `year` / `month` → `dim_tempo` (ancorado em `dt_inicio`, decidido na ingestão Bronze)
- `cod_curso` / `nome_curso` / `modalidade_turma` / `conteudista` / `tematica` → `dim_curso_enap`

**Atributos degenerados:** `sit_matricula`, `cod_turma` / `nome_turma`

**Decisão arquitetural — fato independente:** `codigo_pessoa` é um ID proprietário da plataforma EV.G (Escola Virtual Gov), sem relação documentada com CPF ou `id_servidor_portal`. A abordagem prevista na ADR-009 (rehash SHA-256 para compatibilizar com SIAPE) se mostrou tecnicamente inviável. ENAP é tratado como **fato independente**, mesmo padrão do PEP — sem record linkage nível-servidor com SIAPE/DEPRO (decisão de 03/08/2026, mantida).

**Pendência arquitetural formal — Ponte Capacitação × Mês:** cursos com `dt_inicio`/`dt_fim` em meses diferentes não são "espalhados" no fato transacional (que registra o evento no mês de início, coerente com o restante do modelo). Para métricas de **exposição/estoque** ("quantos servidores em capacitação durante o mês X"), decidiu-se (29/06/2026) que isso será resolvido por uma **tabela ponte/factless separada** na Camada Gold, expandindo `dt_inicio`→`dt_fim` em uma linha por mês de duração — construção física **deferida para a Fase 4**, não faz parte do escopo da Sprint 3.5.

**Bug de tipo descoberto e corrigido (Sprint 3.5, 07/08/2026):** colunas `idade` e `carga_horaria`, declaradas `INTEGER` na External Table Bronze com `autodetect: true`, causavam erro `unsupported Parquet type (BYTE_ARRAY) for GoogleSQL type (INT64)`. Causa raiz: ingestão via `pl.scan_csv()` sem `schema_overrides`, com inferência de tipo feita partição por partição (132 partições mensais) — algumas gravaram as colunas como `Int64`, outras como `String`, gerando schemas Parquet fisicamente inconsistentes entre arquivos. `year`/`month` não afetados (confirmado). Correção aplicada:
1. Script pontual (`scripts/fix_tipos_enap_capacitacao.py`) reescreveu as 132 partições no GCS, forçando `idade`/`carga_horaria` como `string` de forma consistente
2. External Table recriada com schema explícito via `bq mkdef` + edição manual (`infra/external_tables/bronze_enap_capacitacao.json`), sem `autodetect`, com `idade`/`carga_horaria` declaradas `STRING`
3. `stg_enap__capacitacao.sql` já continha `SAFE_CAST(idade AS INT64)` e `SAFE_CAST(carga_horaria AS INT64)` — corrigida uma vírgula faltante na CTE `final`

Validado: `dbt run --select stg_enap__capacitacao` executa sem erro, leitura de `idade`/`carga_horaria`/`year`/`month` confirmada.

---

## 3. Dimensões

### 3.1 `dim_servidor`
- Chave: `id_servidor_portal`
- Atenção: **não é única de fato para registros com `id_servidor_portal = '-11'`**. Confirmado (07/08/2026) como fenômeno transversal a toda a base SIAPE (Ativos: 4.096.137 linhas; Aposentados: 1.746.006 linhas), sempre coincidindo com `situacao_vinculo`/`descricao_cargo = "Sigiloso"`. Qualquer fato ou dimensão construído sobre `id_servidor_portal` herda esta limitação — pendente decisão de tratamento (ex: flag `is_sigiloso`) antes da Fase 4.

### 3.2 `dim_tempo`
- Chave: `year` + `month`
- Possui coluna `ano_mes` (concatenação `year-month`, com padding de 2 dígitos no mês), usada como chave de teste `relationships` composta por fatos que precisam validar a combinação ano+mês de uma vez (ver Fato Vínculo/Ativos, seção 2.2)

### 3.3 `dim_orgao_siape`
- Chave: `cod_org_lotacao`
- **Renomeada de `dim_orgao` (07/08/2026)** para deixar explícito que não é a mesma taxonomia de órgão usada por DEPRO — ver achado abaixo
- Reutilizada por Fato Vínculo/Ativos e Fato Situação de Vínculo
- *(detalhamento pendente — colunas de nome/sigla de órgão a mapear)*

### 3.4 `dim_tipo_vinculo`
- Chave: `cod_tipo_vinculo`
- Reutilizada por Fato Vínculo/Ativos e Fato Situação de Vínculo
- *(detalhamento pendente)*

### 3.5 `dim_orgao_depro`
- Chave: `orgao_codigo_siorg`
- Reutilizada pelos 3 fatos DEPRO (Cargos, Aposentadorias Previstas, Alocação) — mesmas 8 colunas `orgao_*` confirmadas idênticas nas três fontes
- Colunas: `orgao_superior_codigo_siorg`, `orgao_superior_nome`, `orgao_superior_sigla`, `orgao_codigo_siorg`, `orgao_nome`, `orgao_sigla`, `orgao_como_no_raiox_nome`, `orgao_como_no_raiox_sigla`

**Achado — incompatibilidade com `dim_orgao_siape` (Sprint 3.5, 07/08/2026):** verificado apenas **1 código em comum** entre 381 valores distintos de `cod_org_lotacao` (SIAPE) e 198 de `orgao_codigo_siorg` (DEPRO). Comparação visual dos valores brutos descartou diferença de formatação (zeros à esquerda, tipo de dado): são **taxonomias de órgão genuinamente diferentes** — `cod_org_lotacao` é um código legado/interno do SIAPE (5 dígitos, inclui sentinelas negativos como `-1`/`-20`), enquanto `orgao_codigo_siorg` é o código SIORG oficial (6 dígitos, faixa `100xxx`+). Não existe tabela de-para nas fontes atuais.

**Decisão:** `dim_orgao_siape` e `dim_orgao_depro` permanecem **dimensões separadas**, sem tentativa de unificação nesta sprint. Revisão dos 4 editais (Estudos 1, 2, 3) não encontrou requisito explícito de cruzamento linha-a-linha SIAPE↔DEPRO por órgão — Estudos 1 e 3 (mobilidade/trajetória) usam a mobilidade já registrada dentro do próprio SIAPE; Estudo 2 (gastos preditivos) é o único que poderia se beneficiar de cruzar projeção DEPRO com custo real SIAPE por órgão, mas isso seria refinamento futuro do modelo preditivo, não requisito mínimo do edital. **Limitação registrada, não bloqueante** — se o Estudo 2 evoluir para cruzamento órgão a órgão, a lacuna de tabela de-para SIAPE↔SIORG reaparece e precisa ser resolvida naquele momento.

### 3.6 `dim_pessoa_enap`
- Chave: `codigo_pessoa`
- **Independente de `dim_servidor`** — `codigo_pessoa` é ID proprietário da plataforma EV.G, sem relação documentada com `id_servidor_portal`/CPF (ADR-009, rehash SHA-256 avaliado e descartado por inviabilidade técnica). ENAP tratado como fato independente, mesmo padrão do PEP.
- Atributos: `sexo`, `deficiencia`, `raca` (~26% nula — parece campo opcional no formulário, existe resposta ativa "Não quero informar" distinta de nulo, considerar na metodologia do Estudo 7), `nacionalidade`, `uf_pessoa`, `municipio_pessoa`, `instituicao`, `poder`, `esfera`

### 3.7 `dim_curso_enap`
- Chave: `cod_curso`
- Atributos: `nome_curso`, `modalidade_turma`, `conteudista`, `tematica`

*(demais dimensões a preencher conforme novos fatos forem definidos)*

---

## 4. Histórico de decisões

| Data | Decisão | Contexto |
|:-----|:--------|:---------|
| 06/08/2026 | Fato Remuneração definido com grão `servidor + mês`, sem exclusão de duplicidade necessária | Sprint 3.5 — confirmado que Remuneração não tem o mesmo problema de grão que Ativos (ADR-017) |
| 06/08/2026 | Colunas `_dolar` excluídas do Fato Remuneração | Fora do escopo analítico dos editais (moeda de referência é Reais) |
| 06/08/2026 | Fato Vínculo/Ativos resolve ADR-017 via chave surrogate (`sk_vinculo`) sobre 6 colunas, em vez de buscar uma única coluna diferenciadora | Sprint 3.5 — nenhuma coluna de negócio isolada cobria todos os casos de vínculo concomitante investigados |
| 06/08/2026 | Registrado achado de `id_servidor_portal = '-11'` (4.096.137 linhas, servidores sob sigilo legal) como limitação de identificação individual, não como erro de dado | Sprint 3.5 — descoberto ao investigar o Fato Vínculo/Ativos |
| 07/08/2026 | `stg_siape__aposentados` modelado como Fato único "Situação de Vínculo" (não fatos separados por categoria), do tipo Factless | Sprint 3.5 — tabela representa retrato mensal de situação de vínculo (45 categorias), não evento exclusivo de aposentadoria; sem coluna numérica aditiva no schema |
| 07/08/2026 | Grão do Fato Situação de Vínculo resolvido pela mesma `sk_vinculo` (6 colunas) de Ativos, resíduo de 13.088 grupos (0,19%) aceito | Sprint 3.5 — verificado empiricamente: 6.971.465 grupos duplicados no grão simples, reduzidos a 13.088 com as 6 colunas |
| 07/08/2026 | Confirmado que o sentinela `id_servidor_portal = '-11'` é fenômeno transversal da base SIAPE (não exclusivo de Ativos) | Sprint 3.5 — Aposentados tem 1.746.006 linhas com `-11`, exatamente igual à contagem de `situacao_vinculo = 'Sigiloso'` |
| 07/08/2026 | Fato Afastamentos: bug de duplicação exata corrigido via `DISTINCT` no model Silver (`fix:` dedicado) | Sprint 3.5 — 228.704 grupos duplicados eram linhas bit-a-bit idênticas (mesmo `ingestion_timestamp`), não concomitância legítima |
| 07/08/2026 | 3 fatos DEPRO modelados separadamente (Cargos, Aposentadorias Previstas, Alocação), não como fato único genérico | Sprint 3.5 — medem grandezas estruturalmente diferentes, cada um com suas próprias medidas aditivas; forçar fato único exigiria UNION artificial sem base nos editais |
| 07/08/2026 | `dim_orgao` renomeada para `dim_orgao_siape`; nova `dim_orgao_depro` criada como dimensão separada, sem tabela de-para | Sprint 3.5 — apenas 1 código em comum entre 381 (SIAPE) e 198 (DEPRO); taxonomias de órgão confirmadas incompatíveis (código legado vs. SIORG oficial) |
| 07/08/2026 | Fato Alocação DEPRO: agregação `SUM` aplicada no grão `orgao + mês`, absorvendo 385 grupos de linhas paralelas com medidas divergentes | Sprint 3.5 — dicionário oficial da fonte (SEGES/Raio-X) confirma que a tabela não tem dimensão adicional; linhas paralelas violam o grão declarado pela própria fonte, causa raiz não determinável |
| 07/08/2026 | Fato Capacitação ENAP: grão resolvido via `sk_matricula` (chave composta), não `cod_matricula` isolado | Sprint 3.5 — 172 colisões de `cod_matricula` em 19,3M linhas, confirmadas como matrículas genuinamente diferentes (hash truncado sem unicidade global garantida) |
| 07/08/2026 | Bug de tipo `idade`/`carga_horaria` (INT64 vs STRING entre partições) corrigido: reescrita das 132 partições Bronze + External Table recriada sem `autodetect` | Sprint 3.5 — causa raiz: `pl.scan_csv()` sem `schema_overrides`, inferência de tipo inconsistente entre as 132 partições mensais |
| 07/08/2026 | Ponte Capacitação × Mês (factless) formalizada como pendência arquitetural, construção física deferida para a Fase 4 | Sprint 3.5 — decisão de partição por `dt_inicio` já tomada em 29/06; exposição/estoque mensal de cursos multi-mês não resolvida no fato transacional |
| 17/08/2026 | Fato Remuneração fisicamente construído na Fase 4 (Sprint 4.2); FKs de órgão/tipo de vínculo obtidas por enriquecimento via `stg_siape__ativos`, com `NULL` proposital nos ~273k servidores com concomitância de vínculo no mês | Sprint 4.2 — fonte de Remuneração não carrega contexto organizacional; atribuição arbitrária corromperia o fenômeno de mobilidade institucional investigado pelo Estudo 3 (Editais 02 e 04) |
| 17/08/2026 | ADR-017 atualizado: `sk_vinculo` passa de 6 para 8 colunas (`+matricula`, `+situacao_vinculo`, `+cod_uorg_exercicio`); Fato Vínculo/Ativos fisicamente construído na Fase 4 (Sprint 4.3), 96.563.830 linhas, 11/11 testes dbt aprovados | Sprint 4.3 — schema real de `stg_siape__ativos` na Fase 4 mais rico que o disponível na Sprint 3.5; validação incremental em população completa (nunca amostra) reduziu resíduo de 242.588 → 0 grupos duplicados |
| 21/08/2026 | Grão do Fato Situação de Vínculo revalidado na Fase 4 (Sprint 4.4): composição provisória da Sprint 3.5 (6 colunas) descartada; nova chave de 7 colunas (`sk_situacao_vinculo`) fecha 100% do grão em população completa | Sprint 4.4 `stg_siape__aposentados` não possui `cod_uorg_exercicio` (existe apenas em Ativos), tornando a chave de 8 colunas do ADR-017 inaplicável; `cod_tipo_vinculo` (não `situacao_vinculo`) foi a coluna dominante nesta fonte, padrão inverso ao de Ativos; `fct_situacao_vinculo` materializado, 76.314.587 linhas, 13/13 testes dbt aprovados |
| 24/08/2026 | Grão do Fato Afastamentos revalidado na Fase 4 (Sprint 4.5): 5 colunas naturais confirmam 0 grupos duplicados em população completa; decisão de não usar chave surrogate, critério de "grão enxuto" formalizado | Sprint 4.5, `fct_afastamentos` materializado, 9.069.323 linhas, 5/5 testes dbt aprovados; achados da Sprint 3.5 (bug de duplicação exata corrigido, sentinela `-11` ausente, 173 linhas nulas excluídas) todos revalidados sem alteração |