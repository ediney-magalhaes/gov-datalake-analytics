# 📖 Dicionário de Dados e Mapeamento de Fontes

Este documento detalha as fontes oficiais mapeadas para o Data Lake do Governo Federal, descrevendo:

- Estrutura de origem
- Estratégia de ingestão
- Tratamento LGPD
- Regras de transformação para Camada Prata

Documento referente ao **Produto 1 — Descoberta e Mapeamento Técnico (As-Is)**.

---

# 🥇 Camada Bronze — Dados Brutos

---

## 1️⃣ Portal da Transparência — Servidores Ativos (SIAPE)

**Descrição:**  
Base oficial de cadastro funcional e remuneração de servidores ativos do Executivo Federal.

**Formato de Origem:**  
`.zip` contendo arquivos `.csv`

**Codificação:**  
`latin1`

**Separador:**  
`;`

**Frequência:**  
Mensal

**Granularidade:**  
1 linha por servidor ativo por mês de competência.

**Método de Ingestão:**  
- Requisição HTTP com headers customizados  
- Descompactação em memória (`io.BytesIO`)  
- Micro-batching mensal  

### 🔐 LGPD e Segurança

- CPF é dado sensível.
- Aplicação de hash determinístico `SHA-256` **in-flight** (antes da persistência).
- Nenhum dado bruto é salvo em disco local.
- Nomes e cargos mantidos em texto claro, amparados pela Lei de Acesso à Informação (LAI).

---

## 2️⃣ Escola Virtual Gov (ENAP)

**Descrição:**  
Base consolidada de matrículas e histórico de capacitação de servidores públicos.

**Formato de Origem:**  
`.tar.gz` contendo `.gzip` interno com `.csv`

**Codificação:**  
`utf-8`

**Separador:**  
`|` (pipe)

**Frequência:**  
Mensal (consolidado últimos 12 meses)

**Granularidade:**  
1 linha por matrícula em curso por servidor.

**Método de Ingestão:**  
- Extração via API pública
- Descompactação dupla em memória RAM
- Tratamento de delimitador não padrão

### 🔐 LGPD e Segurança

- CPF já fornecido como hash `MD5` na origem.
- Aplicação adicional de `SHA-256` sobre o MD5.
- Padronização criptográfica para permitir JOIN consistente na Camada Ouro.

---

## 3️⃣ SIAPE — Aposentados e Pensionistas

**Descrição:**  
Base oficial de servidores inativos e pensionistas do Executivo Federal.

**Formato de Origem:**  
`.zip` contendo `.csv`

**Codificação:**  
`latin1`

**Separador:**  
`;`

**Frequência:**  
Mensal

**Granularidade:**  
1 linha por servidor inativo por mês de competência.

**Volume Médio:**  
~410.000 registros por mês  
~4.95 milhões registros anuais

### 🔐 LGPD (Bronze)

- CPF convertido para `SHA-256` em memória.
- Persistência apenas da chave criptográfica.
- Pipeline sem armazenamento intermediário local.

---

# 🥈 Camada Prata — Transformação (dbt)

Abaixo, o mapeamento técnico da tabela:

`stg_siape_aposentados`

---

## 🔄 De → Para (Bronze → Prata)

| Bronze | Prata | Regra Aplicada |
|--------|-------|----------------|
| `cpf` | `hash_cpf` | Conversão explícita para STRING. Base da chave composta. |
| `nome` | `nome_servidor` | `TRIM()` + padronização |
| `ORG_LOTACAO` | `orgao_lotacao` | Padronização snake_case |
| `mes_referencia` | `mes_competencia` | Padronização semântica |
| `ID_SERVIDOR_PORTAL` | `id_vinculo` | Identificador do vínculo funcional |
| — | `linha_numero` | `ROW_NUMBER()` para deduplicação |

---

## 🧪 Regra de Unicidade

A unicidade da tabela é garantida pela chave composta:

`hash_cpf + mes_competencia + id_vinculo`

Implementada via:

- `ROW_NUMBER()` particionado
- Teste `unique` no dbt
- Auditoria automática via `dbt test`

---

# 🏛️ Governança

- Fonte → Bronze → Prata documentado
- Transformações tratadas como código (Analytics as Code)
- Testes automatizados garantem integridade histórica
