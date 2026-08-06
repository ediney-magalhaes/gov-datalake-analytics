# ADR 0017: Não aplicação de teste de unicidade em `stg_siape__ativos` — vínculos concomitantes

**Data:** 06 de Agosto de 2026

**Status:** Aceito

**Decisores:** Ediney Magalhães (Analytics Engineering / Data Engineer)

## Contexto
Durante a Sprint 3.4 (testes dbt de qualidade), foi aplicado o teste `dbt_utils.unique_combination_of_columns` sobre `id_servidor_portal + year + month` em `stg_siape__ativos`, partindo da premissa de que a tabela representa um snapshot mensal único por servidor. O teste falhou com 13.348.412 violações.

Investigação incremental sobre a população completa (não amostral) revelou três causas distintas e legítimas de múltiplos registros por servidor/mês:
- Cargo efetivo e função comissionada registrados como linhas separadas (diferenciados por `cod_tipo_vinculo`), reduzindo o volume de 13.348.412 para 562.524
- Múltiplas matrículas SIAPE para o mesmo servidor (ex: dois cargos efetivos simultâneos, comum em hospitais universitários), reduzindo para 208.356 ao combinar `matricula` + `cod_tipo_vinculo`
- Vínculos em múltiplos órgãos simultâneos sob a mesma matrícula (ex: cessão ou dupla lotação institucional), causa ainda não totalmente isolada

Cada nova coluna testada revelou uma nova situação peculiar e legítima do universo de vínculos do serviço público federal, sem indicação de que a busca por uma combinação determinística de colunas chegaria a um grão limpo em tempo hábil.

## Decisão
Não aplicar teste de unicidade (`unique` ou `unique_combination_of_columns`) em `stg_siape__ativos` na camada Silver/staging. A definição do grão de "vínculo único" é uma decisão de modelagem dimensional (Kimball), e será resolvida explicitamente na camada Gold, com regras de negócio definidas para tratar vínculos concomitantes, tema diretamente relacionado ao tratamento de "censuras e riscos competitivos" exigido pelo Estudo 1.

Os demais testes (`not_null` nas colunas essenciais aos estudos, `accepted_range` em `year`/`month`) permanecem aplicados normalmente.

## Alternativas consideradas
- **Continuar empilhando colunas até o teste passar:** Rejeitada. Risco de mascarar casos legítimos ainda não descobertos, sem garantia de término, e resolveria arbitrariamente na Silver uma regra que pertence à modelagem de negócio da Gold.

- **Aplicar teste com `where` de exceção temporária:** Rejeitada. Adicionaria complexidade e falsa sensação de cobertura sem base em regra de negócio real.

- **Não testar unicidade na Silver, resolver grão explicitamente na Gold:** Adotada. Mantém a Silver fiel ao dado bruto (apenas limpo/tipado) e coloca a decisão de negócio onde ela pertence.

## Consequências

**Positivas:**
- Evita decisão de modelagem prematura e possivelmente equivocada na camada errada
- Preserva informação de vínculos concomitantes, relevante para os Estudos 1 e 4 (trajetória e liderança)
- Investigação documentada serve de insumo direto para o desenho da Gold (dimensão de vínculo, não só de servidor)

**Negativas / Trade-offs:**
- `stg_siape__ativos` fica sem proteção automatizada contra duplicação acidental real (ex: reprocessamento indevido) até a Gold existir
- Termo de Homologação da Prata precisa registrar essa ausência de teste como decisão consciente, não omissão

## Validação
Ao desenhar a Gold, definir explicitamente a granularidade da(s) tabela(s) fato de vínculo/servidor, e então aplicar teste de unicidade apropriado naquela camada.