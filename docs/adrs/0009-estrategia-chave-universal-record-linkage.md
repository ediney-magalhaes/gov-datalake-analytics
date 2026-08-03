# ADR 0009: Estratégia de chave universal (Record Linkage)

**Data:** 28 de Março de 2026
**Status:** Aceito
**Autor:** Ediney Magalhães

## Decisão
A chave universal para cruzamento (record linkage) entre as fontes da Fase 1 é o `id_servidor_portal`, presente nas bases do Portal da Transparência (SIAPE) e DEPRO. Não é uma chave real de identidade (não é CPF), mas é o único identificador estável e consistente disponível nas 8 fontes estruturantes inspecionadas (SIAPE ×4, DEPRO ×3, ENAP).

A ENAP não usa `id_servidor_portal` nem qualquer identificador derivado de CPF — usa `codigo_pessoa`, um código anonimizado proprietário da plataforma EV.G, sem relação documentada com o Portal da Transparência ou com CPF. Essa premissa foi verificada em 02/08/2026 junto ao Dicionário de Dados oficial da Escola Virtual Gov, que define `codigo_pessoa` apenas como "código anonimizado que identifica de forma única cada pessoa" — sem qualquer menção a CPF ou hash reversível. Não existe rehash SHA-256 possível: um hash não pode ser recalculado a partir de outro hash já aplicado por terceiros. A ENAP, portanto, **não participa do record linkage** e é tratada como fato independente na modelagem (mesmo tratamento do PEP).

O PEP (`basedosdados.br_mp_pep.cargos_funcoes`) foi inspecionado e confirmado como base agregada por grupo demográfico/organizacional, sem qualquer campo de identificação individual — não participa do record linkage e está fora do escopo desta decisão.

Condições de promoção originalmente definidas — status:
- Condição 1 (todas as bases da Fase 1 com potencial de chave individual ingeridas): **cumprida**
- Condição 2 (auditoria exploratória identificando campos comuns): **cumprida** — via inspeção direta do schema de cada fonte durante a homologação Bronze, substituindo a auditoria DuckDB originalmente planejada

## Alternativas consideradas
- **Apenas `hash_cpf`:** Rejeitado provisoriamente. Bases do Portal da Transparência não entregam CPF real — entregam CPF mascarado ou `id_servidor_portal`. O hash gerado sobre formatos diferentes do mesmo CPF produz códigos distintos, tornando o JOIN impossível entre fontes heterogêneas.

- **Apenas `id_servidor_portal`:** Rejeitado provisoriamente. Esse identificador existe nas bases públicas do Portal da Transparência, mas não há garantia de que estará presente nas bases de APIs restritas (SIAPEcad, SIGEPE, SouGov).

- **Chave composta (`id_servidor_portal` para SIAPE e DEPRO):** Adotada para essas duas fontes. A inspeção completa confirmou que `id_servidor_portal` é o identificador comum entre SIAPE e DEPRO. A hipótese original de estender essa chave à ENAP via rehash SHA-256 foi **descartada em 02/08/2026** após verificação do Dicionário de Dados oficial da fonte: `codigo_pessoa` é um ID proprietário sem relação com CPF, tornando o rehash tecnicamente inviável (não é possível reverter um hash de terceiros para recalcular outro compatível).

## Consequências

**Positivas:**
- Evita a criação de uma chave universal baseada em suposições, prevenindo erros silenciosos de JOIN na Silver que só seriam descobertos na camada Gold.
- Mantém a arquitetura honesta — a decisão só será tomada quando houver evidência real dos dados.
- Protege o projeto de refatoração cara nas camadas Silver e Gold caso a chave escolhida prematuramente se mostre inviável.

**Negativas / Trade-offs:**
- `id_servidor_portal` não é uma chave de identidade real (não é CPF) — se o Portal da Transparência ou o Raio-X alterarem a lógica de geração desse identificador entre versões, o histórico pode quebrar silenciosamente. Risco a monitorar na Fase 5 (Silver).
- ENAP fica fora do record linkage nível-servidor — os estudos de capacitação (Trilhas B/C) não podem cruzar diretamente "curso realizado" com "trajetória de carreira" a nível individual. Estudos com ENAP ficam limitados a análises agregadas (por órgão, UF, tema, período), sem join com SIAPE/DEPRO.

**Risco monitorado:**
- As APIs restritas (SIAPEcad, SIGEPE, SouGov) permanecem bloqueadas (Fase 1) e seu campo de cruzamento ainda não foi verificado. Se, quando desbloqueadas, não entregarem `id_servidor_portal` nem CPF compatível, será necessário avaliar record linkage probabilístico (nome + órgão + data de ingresso) como fallback.
- O PEP (`br_mp_pep.cargos_funcoes`) é uma fonte agregada, sem chave individual — não participa do record linkage e não deve ser forçado a isso em nenhuma modelagem futura.
- **ENAP sem linkage (confirmado, não mais hipótese):** caso um estudo futuro exija cruzar capacitação com dados de RH a nível de servidor, será necessário avaliar linkage probabilístico (nome + UF + idade aproximada), com validação estatística de precisão antes de qualquer uso analítico — conforme exigência do Edital 03 de auditoria do record linkage.