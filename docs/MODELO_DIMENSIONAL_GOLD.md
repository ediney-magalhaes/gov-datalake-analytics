# Modelo Dimensional — Camada Ouro (Gold)

**Projeto:** Data Lake Analytics — Gestão de Pessoal (PNUD BRA/21/011 — MGI/SETE/SGP)
**Sprint de origem:** 3.5 — Modelagem Dimensional Kimball
**Status:** Em construção progressiva

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

**Resolução do ADR-017 (Sprint 3.5, 06/08/2026):** como não existe uma única coluna de negócio capaz de diferenciar todos os casos de vínculo concomitante (cada causa investigada usava uma coluna diferenciadora distinta — `cod_tipo_vinculo`, `matricula`, `cod_org_lotacao`), o grão é resolvido por **chave surrogate técnica**, gerada via `dbt_utils.generate_surrogate_key`:

```sql
{{ dbt_utils.generate_surrogate_key(['id_servidor_portal', 'year', 'month', 'cod_tipo_vinculo', 'matricula', 'cod_org_lotacao']) }} as sk_vinculo
```

`sk_vinculo` passa a ser a chave primária técnica do fato. O teste de unicidade (`unique`/`not_null`) deferido na Silver (ADR-017) deve ser aplicado sobre `sk_vinculo` nesta camada, ao construir o model físico na Fase 4 — não sobre `id_servidor_portal` isoladamente. Qualquer resíduo de duplicidade restante após a chave surrogate deve ser investigado como caso novo, não presumido resolvido.

**Dimensões:**
- `id_servidor_portal` → `dim_servidor`
- `year` / `month` → `dim_tempo`
- `cod_org_lotacao` → `dim_orgao`
- `cod_tipo_vinculo` / `tipo_vinculo` → `dim_tipo_vinculo`

**Achado pendente — valor sentinela em `id_servidor_portal` (Sprint 3.5, 06/08/2026):**
`id_servidor_portal = '-11'` ocorre em **4.096.137 linhas** de `stg_siape__ativos` (~5% da tabela). Não é erro de ingestão: todas essas linhas têm `descricao_cargo = "Sigiloso"` e `situacao_vinculo = "Sigiloso"` — servidores sob sigilo legal (cargos de segurança institucional), cuja identificação real o Portal da Transparência não publica. `-11` é um placeholder da fonte, não um identificador de pessoa.

Consequência: milhões de servidores diferentes compartilham a mesma chave falsa. Isso não quebra `sk_vinculo` (que usa outras colunas além de `id_servidor_portal`), mas invalida `id_servidor_portal` como identificador único de pessoa para todo esse subconjunto. Qualquer análise que dependa de contar/rastrear indivíduos (ex: Estudo 1 — trajetórias, Estudo 8 — liderança) precisa tratar `id_servidor_portal = '-11'` como "não identificável", nunca como uma única pessoa reaparecendo.

**Pendências de verificação (não bloqueantes para esta sprint):**
- Confirmar se o mesmo padrão de sigilo (`-11` ou equivalente) existe em `stg_siape__remuneracao`, `stg_siape__aposentados`, `stg_siape__afastamentos`
- Avaliar se `dim_servidor` precisa de uma regra explícita para tratar registros sigilosos (ex: excluir de contagens de indivíduos únicos, ou marcar com flag `is_sigiloso`)

---

## 3. Dimensões

### 3.1 `dim_servidor`
- Chave: `id_servidor_portal`
- Atenção: não é única de fato para registros com `id_servidor_portal = '-11'` (ver achado de Sigiloso acima)

### 3.2 `dim_tempo`
- Chave: `year` + `month`

### 3.3 `dim_orgao`
- Chave: `cod_org_lotacao`
- *(detalhamento pendente — colunas de nome/sigla de órgão a mapear)*

### 3.4 `dim_tipo_vinculo`
- Chave: `cod_tipo_vinculo`
- *(detalhamento pendente)*

*(demais dimensões a preencher conforme novos fatos forem definidos)*

---

## 4. Histórico de decisões

| Data | Decisão | Contexto |
|:-----|:--------|:---------|
| 06/08/2026 | Fato Remuneração definido com grão `servidor + mês`, sem exclusão de duplicidade necessária | Sprint 3.5 — confirmado que Remuneração não tem o mesmo problema de grão que Ativos (ADR-017) |
| 06/08/2026 | Colunas `_dolar` excluídas do Fato Remuneração | Fora do escopo analítico dos editais (moeda de referência é Reais) |
| 06/08/2026 | Fato Vínculo/Ativos resolve ADR-017 via chave surrogate (`sk_vinculo`) sobre 6 colunas, em vez de buscar uma única coluna diferenciadora | Sprint 3.5 — nenhuma coluna de negócio isolada cobria todos os casos de vínculo concomitante investigados |
| 06/08/2026 | Registrado achado de `id_servidor_portal = '-11'` (4.096.137 linhas, servidores sob sigilo legal) como limitação de identificação individual, não como erro de dado | Sprint 3.5 — descoberto ao investigar o Fato Vínculo/Ativos |