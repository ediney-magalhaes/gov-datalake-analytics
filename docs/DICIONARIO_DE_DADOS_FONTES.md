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

### Atualização de Governança e LGPD (Fase 3)

Para adequação rigorosa à LGPD e para garantir a auditoria de *Record Linkage* (Edital 3), as seguintes regras de negócio foram aplicadas na Camada Bronze durante a ingestão in-memory:

* **`Id_SERVIDOR_PORTAL`**: Definida como a **Chave Primária Oficial** de cruzamento (Record Linkage) para integrações com bases externas do Ministério, garantindo rastreabilidade sem exposição de dados sensíveis.
* **`CPF`**: O dado bruto (que já vinha mascarado da origem como `***.123.456-**`) sofre processo automatizado de **Pseudonimização via Hashing Determinístico (SHA-256)** usando a biblioteca nativa `hashlib` no motor *Polars*, antes da persistência no disco. O formato final da coluna no Data Lake é um código alfanumérico irreversível.
* **`Escolaridade`**: Homologado via *Gap Analysis* que a variável **NÃO EXISTE** nos microdados públicos do Portal da Transparência (apenas no SIAPEcad/SouGov via API restrita).

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

## 4. Portal da Transparência (SIAPE / CGU)
**Padrão de Ingestão:** CSV compactado em ZIP via Motor Polars (`pipeline_bronze_raw_polars`).

| Sistema / Domínio | URL do ZIP Mensal (Ex: 2025/01) | Nome Interno do CSV (Atenção) |
| :--- | :--- | :--- |
| **siape_ativos** | `.../202501_Servidores_SIAPE` | `202501_Cadastro.csv` |
| **siape_remuneracao** | `.../202501_Servidores_SIAPE` | `202501_Remuneracao.csv` |
| **siape_aposentados** | `.../202501_Aposentados_SIAPE` | **`202501_Cadastro.csv`** *(Governo reaproveita o nome dos ativos)* |

---

# Camada Prata — Transformação (dbt)

- As tabelas da Camada Prata passam por tipagem estrita, renomeação semântica e deduplicação técnica.
- Valores nulos críticos tratados via regras de negócio (ex: COALESCE para 0.00 em salários vazios). Campos imputados permanecem rastreáveis via testes de auditoria (dbt tests) para evitar falsos positivos na Camada Ouro

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

---

# Camada Ouro — Data Marts (Consolidação Analítica)

As tabelas da Camada Ouro representam a entrega de valor para o usuário final (Power BI) e respondem aos blocos temáticos do Edital. Nesta camada, os dados da Prata são cruzados, enriquecidos e traduzidos para regras de negócio estabelecidas.

## 1. Blocos 1 e 2: Dinâmicas da Força de Trabalho e Diversidade, Inclusão e Equidade (`mart_servidores_remuneracao`)
- **Descrição**: Tabela analítica (***One Big Table***) que consolida os dados demográficos (raça, sexo, idade), funcionais (cargo, órgão, UF) e financeiros (remuneração bruta e líquida) dos servidores ativos do Executivo Federal.
- **Granularidade**: 1 linha por servidor, por vínculo, por mês de competência.
- **Estratégia FinOps**: Materializada fisicamente como `table` no BigQuery, reduzindo drasticamente o custo de processamento ao evitar o recálculo diário de milhões de linhas durante o consumo pelos painéis de BI.

**Mapeamento e Regras de Negócio (Transformações Ouro)**
| Coluna Ouro | Regra de Transformação Aplicada |
| :--- | :--- |
| raca_cor e sexo | Colunas demográficas importadas da base de cadastro para viabilizar os indicadores do **Bloco 2 (Diversidade e Inclusão)**. |
| `cargo` e `uf_exercicio` | Colunas funcionais importadas da base de cadastro para viabilizar os indicadores do **Bloco 1 (Dinâmicas da Força de Trabalho)**. |
| `remuneracao_bruta` e `liquida` | Valores financeiros unificados via `LEFT JOIN` utilizando uma chave de cruzamento tripla (CPF + Vínculo + Mês). |

**Regras de Qualidade e Contrato de Dados (dbt tests)**
Para assegurar que o Governo não tome decisões baseadas em dados financeiros duplicados ou inconsistentes, esta tabela possui as seguintes travas de auditoria:
- **Integridade Relacional**: A chave de cruzamento primária (`hash_cpf`) possui teste de not_null.
- **Unicidade Complexa (Prevenção de Duplicidade)**: Implementação do teste `unique_combination_of_columns` (pacote ***dbt_utils***) sobre a tríade `[hash_cpf, id_vinculo, mes_competencia]`. Isso garante matematicamente que nenhum servidor apareça recebendo dois salários no mesmo vínculo e no mesmo mês de referência.

## 2. Bloco 3: Competências e Alinhamento Estratégico (`mart_servidores_capacitacao`)
- **Descrição**: Tabela analítica consolidada cruzando o perfil demográfico e funcional dos servidores ativos (SIAPE) com seu histórico de capacitações (ENAP).
- **Granularidade**: 1 linha por matrícula de curso por servidor.
- **Estratégia FinOps**: Materializada fisicamente como table no BigQuery para otimização de performance e redução de custos de leitura (Data Warehouse colunar) durante o consumo pelo painel de BI.

**Mapeamento e Regras de Negócio (Transformações Ouro)**
| Coluna Ouro | Regra de Transformação Aplicada |
| :--- | :--- |
| `tematica_curso` | Tratamento de valores vazios da origem via função `COALESCE`, imputando o valor padrão **'Não Informado'**. |
| `situacao_matricula` | Padronização semântica via `CASE WHEN` para agrupar as diversas nomenclaturas da fonte em 4 categorias oficiais de negócio: **'Concluído'** (Concluida), **'Evadido'** (Desistente, Trancada, Não Concluído, Reprovado) e **'Não Informado'**. |

**Regras de Qualidade e Contrato de Dados (dbt tests)**
Para garantir a consistência e rastreabilidade exigidas no Produto 4, a tabela Ouro possui os seguintes bloqueios de auditoria automatizados:
- **Integridade Relacional**: A chave de cruzamento `hash_cpf` e a coluna `tematica_curso` possuem testes de `not_null`.
- **Governança de Domínio**: A coluna `situacao_matricula` possui um teste estrito de `accepted_values`, garantindo que o banco de dados rejeite qualquer atualização que traga status fora do padrão acordado ('Concluído', 'Em andamento', 'Evadido', 'Não Informado').

