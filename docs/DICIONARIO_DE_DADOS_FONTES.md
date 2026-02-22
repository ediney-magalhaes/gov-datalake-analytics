# Dicionário de Dados e Mapeamento de Fontes

Este documento detalha as fontes oficiais mapeadas para o Data Lake do Governo Federal, descrevendo a estrutura de origem, estratégia de ingestão, conformidade com a LGPD e as regras de transformação para a Camada Prata.

Este documento integra o Produto 1 — Descoberta e Mapeamento Técnico (As-Is).

---

# Camada Bronze — Dados Brutos

---

## 1. Portal da Transparência — Servidores Ativos (SIAPE)

- **Descrição:** Base oficial de cadastro funcional de servidores ativos do Executivo Federal.
- **Formato de Origem:** .zip contendo arquivos .csv
- **Codificação:** latin1
- **Separador:** ; (ponto e vírgula)
- **Frequência:** Mensal
- **Granularidade:** 1 linha por servidor ativo por mês de competência.
- **Método de Ingestão:** Requisição HTTP com headers customizados, descompactação em memória (io.BytesIO) e micro-batching mensal.

### LGPD e Segurança
- CPF é tratado como dado sensível.
- Aplicação de hash determinístico SHA-256 in-flight (antes da persistência).
- Nenhum dado bruto é persistido em disco local (processamento em memória).
- Nomes e cargos mantidos em texto claro, amparados pela Lei de Acesso à Informação (LAI).

---

## 2. Portal da Transparência — Remuneração (SIAPE)

- **Descrição:** Detalhamento de todas as rubricas de pagamento, descontos e verbas indenizatórias.
- **Formato de Origem:** .zip (mesmo pacote do Cadastro) contendo arquivo específico de Remuneracao.csv
- **Codificação:** latin1
- **Separador:** ;
- **Frequência:** Mensal
- **Volume:** ~5,5 milhões de registros (ano base 2025).

### Limpeza de Schema (Whitelisting)
Devido à presença de caracteres especiais, acentos, símbolos monetários e asteriscos nos cabeçalhos originais, foi aplicada uma regra de Expressão Regular (Regex) para normalização das colunas na ingestão:
- **Regra:** `[^A-Z0-9_]` -> Substituição por underline.
- **Resultado:** Nomes de colunas 100% compatíveis com o padrão ANSI SQL do BigQuery.

---

## 3. Escola Virtual Gov (ENAP)

- **Descrição:** Base consolidada de matrículas e histórico de capacitação de servidores públicos.
- **Formato de Origem:** .tar.gz contendo .gzip interno com .csv
- **Codificação:** utf-8
- **Separador:** | (pipe)
- **Frequência:** Mensal (consolidado dos últimos 12 meses).
- **Método de Ingestão:** Extração via API pública com dupla descompactação em memória RAM.

### LGPD e Segurança
- A origem fornece o CPF mascarado em MD5.
- Para garantir a interoperabilidade (JOIN) com as bases do SIAPE, o pipeline reaplica o hash SHA-256 sobre o valor de origem, criando uma chave criptográfica unificada em todo o Data Lake.

---

# Camada Prata — Transformação (dbt)

As tabelas da Camada Prata passam por tipagem estrita, renomeação semântica e deduplicação técnica.

## Mapeamento Técnico Principal (Exemplo: stg_siape_ativos)

| Bronze (Origem) | Prata (Destino) | Regra de Transformação |
|:--- |:--- |:--- |
| CPF | hash_cpf | CAST para STRING + Normalização |
| NOME | nome_servidor | UPPER() e TRIM() para limpeza de strings |
| DESCRICAO_CARGO | cargo_nome | Padronização de nomenclatura |
| MES_REFERENCIA | mes_competencia | Conversão para padrão DATE ou Competência |
| ID_SERVIDOR_PORTAL | id_vinculo | Mantido como identificador único de vínculo |

## Regras de Qualidade e Unicidade

A integridade dos dados na Camada Prata é validada via dbt test e tratada no processo de modelagem:

1. **Unicidade:** Chave composta por `hash_cpf`, `mes_competencia` e `id_vinculo`.
2. **Deduplicação:** Aplicação de `ROW_NUMBER()` para garantir que apenas o registro mais recente de cada competência seja processado.
3. **Observabilidade de Nulos:** Identificadores nulos detectados na Camada Bronze são tratados na Camada Prata para garantir a persistência da volumetria original. Campos mandatórios ausentes são imputados com o valor padrão 'NAO INFORMADO' ou isolados via testes de qualidade para auditoria posterior, evitando a perda de registros durante a transição de camadas.


---

# Governança e Transparência

- **Analytics as Code:** Todas as transformações são versionadas via Git.
- **Linhagem:** O fluxo Fonte -> Bronze -> Prata é documentado automaticamente via dbt docs.
- **Auditoria:** Logs de performance e volumetria são gerados a cada ciclo de ingestão e transformação.