# Analytics Gov — Transformação de Dados (dbt)

Este diretório contém o projeto dbt Core responsável pelas transformações da Camada Prata (Staging) e da Camada Ouro (Marts Analíticos) do Data Lake do Governo Federal.

A arquitetura foi desenhada para:
- Padronizar, tipar e limpar dados brutos (Camada Bronze).
- Garantir integridade, unicidade e rastreabilidade.
- Aplicar regras técnicas de deduplicação e imputação segura.
- Consolidar as informações em One Big Tables (OBTs) para consumo otimizado em ferramentas de BI.

---

## Como Executar o Projeto

### 1. Instalar Dependências
Na primeira execução, instale os pacotes necessários (ex: dbt_utils):

```bash
dbt deps
```

### 2. Executar Transformações
Materialize as views na Camada Prata e tabelas na Camada Ouro no BigQuery:
```bash
dbt run
```

### 3. Executar Testes de Qualidade
Valide a integridade, unicidade e conformidade dos dados processados:
```bash
dbt test
```

### 4. Gerar e Visualizar a Documentação (Catálogo e Linhagem)
Para gerar o dicionário de dados interativo e visualizar o Grafo de Linhagem (Lineage Graph):
```bash
dbt docs generate
dbt docs serve
```

---

## Regras de Engenharia e Governança
**Deduplicação Inteligente**
Uso de Window Functions (`ROW_NUMBER()`) com partição por `hash_cpf`, `mes_competencia` e `id_vinculo`, garantindo unicidade matemática mesmo em caso de reenvios duplicados pelos sistemas governamentais.

**Padronização e Tipagem**

- Conversão rigorosa de colunas para `snake_case`.
- Tipagem explícita (`CAST` para `DATE`, `NUMERIC`, `STRING`).
- Limpeza de strings anômalas (ex: `TRIM()` em bases da ENAP, `REPLACE()` em salários).

**Governança e Imputação Segura**
Valores nulos críticos são tratados via regras de negócio (ex: uso de `COALESCE` para 0.00 em salários vazios na origem). Campos imputados permanecem rastreáveis via testes de auditoria para evitar falsos positivos nos painéis finais.

**Estratégia FinOps (Camada Ouro)**
As tabelas finais (OBTs) são materializadas fisicamente (`table`). O design prevê a evolução para materialização incremental (estratégia `insert_overwrite` particionada por `mes_referencia`) para garantir idempotência e redução drástica de custos de scan no BigQuery.

---

## Estrutura do Projeto
```bash
O projeto segue as melhores práticas de organização de diretórios do dbt:
models/
├── staging/                           # Camada Prata (Limpeza e Padronização)
│   ├── _stg_siape__models.yml         # Contratos, testes e dicionário (Prata)
│   ├── stg_siape_ativos.sql
│   ├── stg_siape_aposentados.sql
│   ├── stg_siape_remuneracao.sql
│   └── stg_enap_capacitacao.sql
│
└── marts/                             # Camada Ouro (Regras de Negócio e BI)
    ├── _marts__models.yml             # Contratos, testes e dicionário (Ouro)
    └── mart_servidores_remuneracao.sql # OBT Consolidada (Ativos + Folha)
```

---

## Status e Próximos Passos
- [x] **Produto 3**: Camada Prata estruturada e testada (SIAPE e ENAP).

- [x] **Produto 4 (Blocos 1 e 2)**: Criação da OBT cruzando Servidores e Remuneração para análise de equidade e dinâmica da força de trabalho.

- [ ] **Produto 4 (Bloco 3)**: Desenvolvimento do Data Mart cruzando dados de RH com a base da ENAP para análise de competências e capacitação contínua.