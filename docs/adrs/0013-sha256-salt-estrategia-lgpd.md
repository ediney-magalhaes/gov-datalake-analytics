# ADR-013: SHA-256 + Salt como estratégia de pseudonimização LGPD

**Data:** 18 de Abril de 2026
**Status:** Aceito
**Autor:** Ediney Magalhães

## Contexto
O projeto processa dados pessoais sensíveis de servidores públicos federais (CPF, nome, matrícula). A Lei Geral de Proteção de Dados (LGPD — Lei 13.709/2018) exige que esses dados sejam protegidos antes da persistência em qualquer camada do Data Lake.

O CPF é o principal identificador pessoal presente nas bases. Algumas fontes entregam o CPF mascarado (Portal da Transparência), outras entregam o CPF real (APIs restritas). Em ambos os casos, é necessária uma estratégia de pseudonimização que:
- Seja irreversível para proteção do titular
- Seja determinística para permitir JOINs entre bases
- Seja aplicada antes da persistência em disco ou nuvem

## Decisão
Adotar SHA-256 com Salt estático como algoritmo de pseudonimização do CPF, aplicado in-flight durante a ingestão no motor Polars, antes da gravação do arquivo Parquet.
O Salt é gerenciado via variável de ambiente (.env) e nunca versionado no repositório Git.

## Alternativas consideradas
- **SHA-256 sem Salt:** Rejeitado. Vulnerável a ataques de dicionário — um atacante pode gerar hashes de todos os CPFs possíveis (número finito) e reverter a pseudonimização por força bruta.

- **MD5:** Rejeitado. Algoritmo com colisões conhecidas e considerado criptograficamente fraco. Incompatível com requisitos de segurança de projetos governamentais.

- **Criptografia reversível (AES):** Rejeitado. Criptografia reversível não é pseudonimização — exige gestão de chaves complexa e não atende ao princípio de minimização de dados da LGPD para o contexto analítico.

- **Tokenização via serviço externo:** Rejeitado. Introduz dependência de serviço externo, custo adicional e latência no pipeline — incompatível com a premissa de custo zero.

## Consequências
**Positivas:**
- Conformidade com a LGPD antes da persistência em qualquer camada do Data Lake
- Determinístico — o mesmo CPF sempre gera o mesmo hash, permitindo JOINs entre bases pseudonimizadas
- Salt protege contra ataques de dicionário e força bruta
- Implementado via biblioteca nativa Python (hashlib) — sem dependência externa

**Negativas / Trade-offs:**
- O Salt estático precisa ser custodiado com segurança — sua perda impossibilita a reprodução dos hashes históricos
- Bases que entregam CPF mascarado (ex: Portal da Transparência com formato ***.123.456-**) geram hash diferente do CPF real — este é o problema central da 
  ADR-009 que ainda está Proposta

**Dependência:**
- O valor do HASH_SALT deve ser definido uma única vez e nunca alterado após a primeira ingestão — mudança posterior invalida todos os hashes existentes no Lake