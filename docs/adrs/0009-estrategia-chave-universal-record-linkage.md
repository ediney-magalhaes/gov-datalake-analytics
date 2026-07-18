# ADR 0009: Estratégia de chave universal (Record Linkage)

**Data:** 28 de Março de 2026
**Status:** Aceito
**Autor:** Ediney Magalhães

## Decisão
A chave universal para cruzamento (record linkage) entre as fontes da Fase 1 é o `id_servidor_portal`, presente nas bases do Portal da Transparência (SIAPE) e DEPRO. Não é uma chave real de identidade (não é CPF), mas é o único identificador estável e consistente disponível nas 8 fontes estruturantes inspecionadas (SIAPE ×4, DEPRO ×3, ENAP).

A ENAP não usa `id_servidor_portal` nativamente — usa CPF mascarado em MD5 — e requer rehash SHA-256 para join, conforme já registrado no Inventário de Fontes.

O PEP (`basedosdados.br_mp_pep.cargos_funcoes`) foi inspecionado e confirmado como base agregada por grupo demográfico/organizacional, sem qualquer campo de identificação individual — não participa do record linkage e está fora do escopo desta decisão.

Condições de promoção originalmente definidas — status:
- Condição 1 (todas as bases da Fase 1 com potencial de chave individual ingeridas): **cumprida**
- Condição 2 (auditoria exploratória identificando campos comuns): **cumprida** — via inspeção direta do schema de cada fonte durante a homologação Bronze, substituindo a auditoria DuckDB originalmente planejada

## Alternativas consideradas
- **Apenas `hash_cpf`:** Rejeitado provisoriamente. Bases do Portal da Transparência não entregam CPF real — entregam CPF mascarado ou `id_servidor_portal`. O hash gerado sobre formatos diferentes do mesmo CPF produz códigos distintos, tornando o JOIN impossível entre fontes heterogêneas.

- **Apenas `id_servidor_portal`:** Rejeitado provisoriamente. Esse identificador existe nas bases públicas do Portal da Transparência, mas não há garantia de que estará presente nas bases de APIs restritas (SIAPEcad, SIGEPE, SouGov).

- **Chave composta (`id_servidor_portal` + rehash SHA-256 para ENAP):** Adotada. A inspeção completa das 8 fontes estruturantes confirmou que `id_servidor_portal` é o identificador comum entre SIAPE e DEPRO. A ENAP exige uma etapa de rehash (MD5 → SHA-256) para se juntar ao mesmo espaço de chaves. Esta é, na prática, uma chave "quase-universal com adaptação por fonte", não uma chave composta multi-campo como se cogitava originalmente.

## Consequências

**Positivas:**
- Evita a criação de uma chave universal baseada em suposições, prevenindo erros silenciosos de JOIN na Silver que só seriam descobertos na camada Gold.
- Mantém a arquitetura honesta — a decisão só será tomada quando houver evidência real dos dados.
- Protege o projeto de refatoração cara nas camadas Silver e Gold caso a chave escolhida prematuramente se mostre inviável.

**Negativas / Trade-offs:**
- `id_servidor_portal` não é uma chave de identidade real (não é CPF) — se o Portal da Transparência ou o Raio-X alterarem a lógica de geração desse identificador entre versões, o histórico pode quebrar silenciosamente. Risco a monitorar na Fase 5 (Silver).
- A etapa de rehash SHA-256 da ENAP adiciona uma transformação extra nos modelos de staging do dbt — precisa ser documentada como regra de negócio explícita, não implícita no código.

**Risco monitorado:**
- As APIs restritas (SIAPEcad, SIGEPE, SouGov) permanecem bloqueadas (Fase 1) e seu campo de cruzamento ainda não foi verificado. Se, quando desbloqueadas, não entregarem `id_servidor_portal` nem CPF compatível, será necessário avaliar record linkage probabilístico (nome + órgão + data de ingresso) como fallback.
- O PEP (`br_mp_pep.cargos_funcoes`) é uma fonte agregada, sem chave individual — não participa do record linkage e não deve ser forçado a isso em nenhuma modelagem futura.
