# ADR 0009: Estratégia de chave universal (Record Linkage)

**Data:** 28 de Março de 2026
**Status:** Proposto
**Autor:** Ediney Magalhães

## Decisão
A definição da chave universal é postergada até a conclusão da ingestão de todas as bases da Fase 1. Somente após a inspeção exploratória dos campos identificadores disponíveis em cada fonte será possível definir com segurança a estratégia de cruzamento.
Esta ADR será promovida para "Aceito" quando as duas condições abaixo forem cumpridas:
- Condição 1: todas as bases da Fase 1 ingeridas na Bronze Normalized
- Condição 2: auditoria exploratória via DuckDB identificando campos comuns entre as fontes (id_servidor_portal, CPF, matrícula ou outro)

## Decisão
Fazer avaliação das bases após ingestão para definição dos campos que irão compor a chave composta

## Alternativas consideradas
- **Apenas `hash_cpf`:** Rejeitado provisoriamente. Bases do Portal da Transparência não entregam CPF real — entregam CPF mascarado ou `id_servidor_portal`. O hash gerado sobre formatos diferentes do mesmo CPF produz códigos distintos, tornando o JOIN impossível entre fontes heterogêneas.

- **Apenas `id_servidor_portal`:** Rejeitado provisoriamente. Esse identificador existe nas bases públicas do Portal da Transparência, mas não há garantia de que estará presente nas bases de APIs restritas (SIAPEcad, SIGEPE, SouGov).

- **Chave composta:** Alternativa mais promissora, porém depende da inspeção dos campos reais disponíveis em cada fonte após a ingestão completa da Fase 1. Será avaliada quando as condições desta ADR forem cumpridas.

## Consequências

**Positivas:**
- Evita a criação de uma chave universal baseada em suposições, prevenindo erros silenciosos de JOIN na Silver que só seriam descobertos na camada Gold.
- Mantém a arquitetura honesta — a decisão só será tomada quando houver evidência real dos dados.
- Protege o projeto de refatoração cara nas camadas Silver e Gold caso a chave escolhida prematuramente se mostre inviável.

**Negativas / Trade-offs:**
- A Fase 5 (Silver) não pode ser iniciada enquanto esta ADR permanecer como "Proposto". É um bloqueio intencional e consciente.
- Os modelos dbt de staging que fazem JOIN entre fontes distintas ficam com a lógica de chave indefinida até a promoção desta ADR.

**Risco monitorado:**
- Se as APIs restritas (SIAPEcad, SIGEPE, SouGov) não entregarem nenhum campo em comum com o `id_servidor_portal` do Portal da Transparência, será necessário avaliar estratégias alternativas como record linkage probabilístico por nome + órgão + data de ingresso.
