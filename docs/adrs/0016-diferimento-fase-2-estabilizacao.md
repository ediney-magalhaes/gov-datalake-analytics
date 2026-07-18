# ADR 0016: Diferimento da Fase 2 (Estabilização) para execução paralela com a Fase 3

**Data:** 18 de Julho de 2026

**Status:** Aceito

**Decisores:** Ediney Magalhães (Analytics Engineering / Data Engineer)

## Contexto
O Roadmap original previa a Fase 2 (Estabilização da Ingestão com: contract drift, controle de volumetria, logs estruturados JSON, correção do bug de dual logging) como pré-requisito formal antes da Fase 3 (Reconstrução da Camada Silver via dbt Core).

Com a Camada Bronze homologada em 11/07/2026, os 8 assets estruturantes (SIAPE, DEPRO, ENAP) estão gravados e estáveis no GCS. Esses dados não sofrerão nova execução do pipeline de ingestão no curto prazo, a próxima execução só ocorrerá quando novas partições históricas forem publicadas pelas fontes originais (ciclo anual/mensal) ou quando novas fontes forem adicionadas.

Os itens da Fase 2 resolvem problemas de **confiabilidade de execuções repetidas** do pipeline de ingestão. Como o pipeline não vai rodar de novo no curto prazo, esses itens não protegem nem bloqueiam o trabalho da Fase 3, que consome os dados já gravados na Bronze.

## Decisão
A Fase 2 é diferida para execução em paralelo com a Fase 3, com exceção do bug de dual logging, corrigido de forma pontual antes do início da Fase 3 por ser um ajuste rápido e não relacionado a execuções futuras.

Os demais itens (validação de contract drift, controle de volumetria, logs estruturados JSON) serão retomados quando uma das condições abaixo ocorrer:
- Necessidade de nova execução do pipeline de ingestão (nova partição histórica publicada, ou nova fonte adicionada à Bronze)
- Os Produtos analíticos (Tracks B e C) indicarem, ao final da Camada Gold, que o pipeline precisa continuar ativo para atualização periódica dos dados

Se os resultados dos estudos analíticos forem satisfatórios com o dado atualmente ingerido (sem necessidade de atualização periódica), a Fase 2 pode ser formalmente encerrada sem execução completa, documentando-se essa decisão como dívida técnica consciente e sem impacto nos produtos entregues.

## Alternativas consideradas
- **Executar a Fase 2 por completo antes da Fase 3:** Rejeitada. Atrasaria o início do dbt Core sem proteger nada que a Silver efetivamente consome (dados já gravados e estáticos).

- **Ignorar a Fase 2 permanentemente:** Rejeitada. Os itens continuam válidos caso o pipeline precise rodar de novo, descartá-los perderia trabalho de diagnóstico já feito (bug de dual logging já identificado, contract drift já nomeado como risco na tabela de riscos técnicos do Roadmap).

- **Diferir a Fase 2 para paralelo com a Fase 3, exceto o bug de dual logging:** Adotada. Prioriza velocidade de entrega dos produtos analíticos sem descartar a estabilização, condicionando sua retomada a critérios objetivos (nova execução do pipeline ou necessidade identificada nos produtos).

## Consequências

**Positivas:**
- Acelera o início da Fase 3 (Silver/dbt), que é o caminho crítico para desbloquear os Tracks B e C (Editais 02, 03, 04).
- Evita investimento em estabilização de um pipeline que pode não precisar rodar de novo.
- Mantém rastreabilidade da decisão e não é uma omissão, é uma escolha documentada com critério de retomada.

**Negativas / Trade-offs:**
- Se o pipeline precisar rodar antes do esperado (ex: correção urgente em uma fonte), os riscos de contract drift e falta de logs estruturados voltam a estar ativos sem mitigação.
- A tabela de riscos técnicos do Roadmap (Seção 6) permanece com "Inconsistência de schemas" e "Instabilidade de APIs" como riscos parcialmente mitigados, não eliminados.

**Risco monitorado:**
- Se uma fonte já homologada (SIAPE, DEPRO, ENAP) publicar uma nova partição histórica antes da Fase 2 ser retomada, a ingestão dessa partição deve ser tratada como exceção manual, com validação de schema feita manualmente até que a validação automatizada de contract drift exista.

## Validação
- Ao final da Camada Gold, revisar se os Produtos analíticos (Tracks B e C) precisam de atualização periódica dos dados.
- Se sim: retomar a Fase 2 formalmente antes de qualquer novo backfill.
- Se não: encerrar a Fase 2 com nota de dívida técnica consciente, sem novo backfill previsto.