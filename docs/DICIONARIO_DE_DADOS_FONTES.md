# Dicionário de Dados e Mapeamento de Fontes

Este documento detalha as fontes oficiais mapeadas para o Data Lake do Governo Federal, descrevendo a estrutura de origem, estratégia de ingestão, conformidade com a LGPD e as regras de transformação para a Camada Prata.

Este documento integra o Produto 1 — Descoberta e Mapeamento Técnico (As-Is).

> **Nota:** Este documento está em construção progressiva. As seções de Camada Prata e Camada Ouro serão detalhadas na sessão de Documentação Reversa ao final da Fase de Engenharia.

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
- **Método de Ingestão:** Requisição HTTP com headers customizados, descompactação em memória (io.BytesIO) e micro-batching mensal via Dagster (asset: `siape_ativos`).

### Governança e LGPD (Fase 1)

Para adequação rigorosa à LGPD e para garantir a auditoria de *Record Linkage* (Edital 3), as seguintes regras de negócio foram aplicadas na Camada Bronze durante a ingestão in-memory:

* **`Id_SERVIDOR_PORTAL`**: Definida como a **Chave Primária Oficial** de cruzamento (Record Linkage) para integrações com bases externas do Ministério, garantindo rastreabilidade sem exposição de dados sensíveis.
* **`CPF`**: O dado bruto (que já vinha mascarado da origem como `***.123.456-**`) sofre processo automatizado de **Pseudonimização via Hashing Determinístico (SHA-256 + Salt)** usando a biblioteca nativa `hashlib` no motor Polars, antes da persistência no GCS. O formato final da coluna no Data Lake é um código alfanumérico irreversível.
* **`Escolaridade`**: Homologado via *Gap Analysis* que a variável **NÃO EXISTE** nos microdados públicos do Portal da Transparência (apenas no SIAPEcad/SouGov via API restrita).

---

## 2. Portal da Transparência — Remuneração (SIAPE)

- **Descrição:** Detalhamento de todas as rubricas de pagamento, descontos e verbas indenizatórias.
- **Formato de Origem:** .zip (mesmo pacote do Cadastro) contendo arquivo específico de Remuneracao.csv
- **Codificação:** latin1
- **Separador:** ;
- **Frequência:** Mensal
- **Volume:** ~5,5 milhões de registros (ano base 2025).
- **Método de Ingestão:** Requisição HTTP com headers customizados, descompactação em memória (io.BytesIO) via Dagster (asset: `siape_remuneracao`).

### Limpeza de Schema (Whitelisting)
Devido à presença de caracteres especiais, acentos, símbolos monetários e asteriscos nos cabeçalhos originais, foi aplicada uma regra de Expressão Regular (Regex) para normalização das colunas na ingestão:
- **Regra:** `[^A-Z0-9_]` -> Substituição por underline.
- **Resultado:** Nomes de colunas 100% compatíveis com o padrão snake_case/ANSI SQL persistidos no GCS.

---

## 3. Portal da Transparência — Aposentados e Pensionistas (SIAPE)

- **Descrição:** Cadastro de aposentados e pensionistas do Executivo Federal.
- **Formato de Origem:** .zip contendo arquivo .csv
- **Codificação:** latin1
- **Separador:** ;
- **Frequência:** Mensal
- **Método de Ingestão:** Requisição HTTP com headers customizados, descompactação em memória (io.BytesIO) via Dagster (asset: `siape_aposentados`).
- **Atenção:** O arquivo interno do ZIP possui o mesmo nome do Cadastro de Ativos (`{ano}{mes}_Cadastro.csv`) — diferenciação feita exclusivamente pela URL de download (`Aposentados_SIAPE` vs `Servidores_SIAPE`).

---

## 4. Portal da Transparência — Afastamentos (SIAPE)

- **Descrição:** Registro de afastamentos de servidores ativos do Executivo Federal.
- **Formato de Origem:** .zip (mesmo pacote do Cadastro de Ativos) contendo arquivo específico de Afastamentos.csv
- **Codificação:** latin1
- **Separador:** ;
- **Frequência:** Mensal
- **Método de Ingestão:** Requisição HTTP com headers customizados, descompactação em memória (io.BytesIO) via Dagster (asset: `siape_afastamentos`).

---

## 5. DEPRO — Alocação, Cargos e Aposentadorias

- **Descrição:** Base do Departamento de Estudos e Políticas do Estado, da Previdência e do Trabalho (DEPRO/MGI), contendo projeções e registros de alocação, cargos e aposentadorias de servidores por órgão.
- **Formato de Origem:** .zip contendo arquivos .csv
- **Codificação:** latin1
- **Separador:** ;
- **Frequência:** Mensal
- **Método de Ingestão:** Requisição HTTP com headers customizados, descompactação em memória (io.BytesIO) via Dagster.

| Asset | Descrição |
|:------|:----------|
| `depro_alocacao` | Alocação de servidores por órgão |
| `depro_cargos` | Cargos de servidores por órgão |
| `depro_aposentadorias` | Projeção de aposentadorias por órgão |

---

## 6. Escola Virtual Gov (ENAP)

- **Descrição:** Base consolidada de matrículas e histórico de capacitação de servidores públicos.
- **Formato de Origem:** .tar.gz contendo .gzip interno com .csv (dupla descompactação)
- **Codificação:** utf-8
- **Separador:** | (pipe)
- **Frequência:** Mensal (consolidado dos últimos 12 meses).
- **Método de Ingestão:** Download de arquivo via HTTP com dupla descompactação em memória RAM via Dagster (asset: `enap_capacitacao`).

### LGPD e Segurança
- A origem fornece o CPF mascarado em MD5.
- Para garantir a interoperabilidade (JOIN) com as bases do SIAPE, o pipeline reaplica o hash SHA-256 + Salt sobre o valor de origem, criando uma chave criptográfica unificada em todo o Data Lake.

---

## 7. Fontes Previstas — Fase 1 (Pendentes)

| Fonte | Descrição | Status |
|:------|:----------|:------:|
| Observatório de Pessoal | Painéis e produtos analíticos do MGI | ⏳ Pendente |
| PEP | Base de desempenho e avaliação | ⏳ Pendente |
| ACT Lemann | Base de competências | ⏳ Disponibilidade não confirmada |
| Pesquisa Vozes | Pesquisa de clima organizacional | ⏳ Pendente |
| Base de Currículos | Perfil profissional dos servidores | ⏳ Pendente |

---

## 8. Padrão de URLs e Arquivos Internos

**Padrão de Ingestão:** CSV compactado em ZIP via Motor Polars + Requests (`motor_ingestao.py`).

| Asset | URL do ZIP Mensal (Ex: 2025/01) | Nome Interno do CSV |
|:------|:--------------------------------|:--------------------|
| `siape_ativos` | `.../202501_Servidores_SIAPE` | `202501_Cadastro.csv` |
| `siape_remuneracao` | `.../202501_Servidores_SIAPE` | `202501_Remuneracao.csv` |
| `siape_afastamentos` | `.../202501_Servidores_SIAPE` | `202501_Afastamentos.csv` |
| `siape_aposentados` | `.../202501_Aposentados_SIAPE` | `202501_Cadastro.csv` *(mesmo nome dos ativos)* |

---

# Camada Prata — Transformação (dbt)

- As tabelas da Camada Prata passam por tipagem estrita, renomeação semântica e deduplicação técnica.
- Valores nulos críticos tratados via regras de negócio (ex: COALESCE para 0.00 em salários vazios). Campos imputados permanecem rastreáveis via testes de auditoria (dbt tests) para evitar falsos positivos na Camada Ouro.

## Mapeamento Técnico Principal (Exemplo: stg_siape_ativos)

| Bronze (Origem) | Prata (Destino) | Regra de Transformação |
|:----------------|:----------------|:-----------------------|
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
- **Linhagem:** O fluxo Fonte → Bronze → Prata é documentado automaticamente via dbt docs.
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
|:------------|:--------------------------------|
| `raca_cor` e `sexo` | Colunas demográficas importadas da base de cadastro para viabilizar os indicadores do **Bloco 2 (Diversidade e Inclusão)**. |
| `cargo` e `uf_exercicio` | Colunas funcionais importadas da base de cadastro para viabilizar os indicadores do **Bloco 1 (Dinâmicas da Força de Trabalho)**. |
| `remuneracao_bruta` e `liquida` | Valores financeiros unificados via `LEFT JOIN` utilizando uma chave de cruzamento tripla (CPF + Vínculo + Mês). |

**Regras de Qualidade e Contrato de Dados (dbt tests)**

- **Integridade Relacional**: A chave de cruzamento primária (`hash_cpf`) possui teste de not_null.
- **Unicidade Complexa (Prevenção de Duplicidade)**: Implementação do teste `unique_combination_of_columns` (pacote ***dbt_utils***) sobre a tríade `[hash_cpf, id_vinculo, mes_competencia]`.

## 2. Bloco 3: Competências e Alinhamento Estratégico (`mart_servidores_capacitacao`)
- **Descrição**: Tabela analítica consolidada cruzando o perfil demográfico e funcional dos servidores ativos (SIAPE) com seu histórico de capacitações (ENAP).
- **Granularidade**: 1 linha por matrícula de curso por servidor.
- **Estratégia FinOps**: Materializada fisicamente como `table` no BigQuery para otimização de performance e redução de custos de leitura durante o consumo pelo painel de BI.

**Mapeamento e Regras de Negócio (Transformações Ouro)**

| Coluna Ouro | Regra de Transformação Aplicada |
|:------------|:--------------------------------|
| `tematica_curso` | Tratamento de valores vazios da origem via função `COALESCE`, imputando o valor padrão **'Não Informado'**. |
| `situacao_matricula` | Padronização semântica via `CASE WHEN` para agrupar as diversas nomenclaturas da fonte em categorias oficiais: **'Concluído'**, **'Em andamento'**, **'Evadido'**, **'Não Informado'**. |

**Regras de Qualidade e Contrato de Dados (dbt tests)**

- **Integridade Relacional**: A chave de cruzamento `hash_cpf` e a coluna `tematica_curso` possuem testes de `not_null`.
- **Governança de Domínio**: A coluna `situacao_matricula` possui um teste estrito de `accepted_values`, garantindo que o banco de dados rejeite qualquer atualização que traga status fora do padrão acordado.