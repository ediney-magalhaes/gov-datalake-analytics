# Projeto Data Lake - Gestão de Pessoal (Governo Federal)

Projeto técnico de Arquitetura de Dados em Cloud para ingestão, tratamento e disponibilização de dados públicos do Governo Federal (folha de pagamento, aposentadorias e capacitação do executivo federal).

O projeto como um todo abrangerá o desenvolvimento de processos de governança e de infraestrutura digital pública que garantam a interoperabilidade, a atualização contínua e o uso analítico das informações, no âmbito da Secretaria Extraordinária para a Transformação do Estado (SETE) e da Secretaria de Gestão de Pessoas (SGP), vinculada ao Projeto BRA/21/011 – Fortalecimento de Capacidades para Modernização e Aprimoramento da Gestão Estatal da União.

---

## Contexto e Desafio de Negócio

O Poder Executivo Federal gera diariamente uma vasta quantidade de dados sobre a gestão de seus servidores. Historicamente, essas informações encontram-se dispersas em múltiplos sistemas (SIAPE, SouGov, SIAPEcad, SIGEPE, entre outros), com estruturas heterogêneas e limitada interoperabilidade, o que dificulta análises consistentes e o uso em tempo real para subsidiar decisões.

### O Problema
A extração manual ou semiautomatizada dessas bases fragmentadas compromete a agilidade, confiabilidade e abrangência das análises, ressaltando a necessidade de desenvolvimento de soluções integradas, automatizadas e seguras, que promovam a unificação das bases de dados e facilitem a governança da informação no âmbito do governo federal.

### A Solução
Em alinhamento com a Estratégia Federal de Governo Digital (Portaria SGD/MGI nº 6.618/2024), este projeto constrói uma infraestrutura digital pública unificada. Adotando princípios inspirados na arquitetura medallion (camadas bronze, silver e gold), que organiza os dados em níveis crescentes de qualidade e tratamento: desde a ingestão bruta e imutável (bronze), passando por estruturas refinadas e confiáveis para análise (silver), até vistas analíticas consolidadas voltadas à tomada de decisão (gold).

O pipeline desenvolvido foca em resiliência e segurança:
- Automatiza a coleta de dados de múltiplas fontes oficiais (APIs paginadas e arquivos massivos).
- Cada etapa do pipeline incorpora mecanismos automatizados de anonimização ou pseudonimização de dados pessoais sensíveis, em conformidade com a LGPD, integrando esses procedimentos diretamente aos processos de ingestão e transformação.
- Entrega bases consolidadas para subsidiar análises preditivas, estudos de trajetórias funcionais, diversidade e mapeamento de competências.

---

## Decisões Arquiteturais (Evolução da Ingestão e Governança)

Para garantir a escalabilidade exigida e a aprovação em auditorias de conformidade, a arquitetura de ingestão (Camada Bronze) foi reestruturada adotando o padrão *Modern Data Stack*:

* **Processamento em Memória (Otimizado):** Substituição do Pandas pelo **Polars**. O processamento vetorizado evita erros de falta de memória (OOM) ao descompactar e ler dezenas de gigabytes de arquivos ZIP governamentais.
* **Framework de Extração (APIs):** Adoção do **dlt (Data Load Tool)** para automatizar, paralelizar e padronizar as requisições em APIs complexas (como SIAPEcad e SouGov). Implementação de resiliência de rede (Graceful Degradation) com blocos `try...except` para suportar instabilidades nos firewalls do Governo (Serpro).
* **Armazenamento Colunar (Data Lake):** Transição de bancos locais/memória para persistência física no formato **Parquet** via destino `filesystem` nativo do dlt. Isso garante alta compressão e atua como backup imutável da Camada Bronze, pronto para migração Cloud (Google Cloud Storage / AWS S3).
* **Segurança In-Flight (LGPD):** Implementação de Hashing Determinístico (SHA-256) na coluna CPF utilizando a biblioteca nativa `hashlib` durante o processamento in-memory, antes da persistência no disco.
* **Governança Operacional:** Implementação de **Dual Logging** (Terminal + `.log` local via biblioteca nativa `logging`), registrando a saúde, latência e falhas de cada extração, provendo total rastreabilidade.
* **Orquestrador Centralizado:** Implementação do Padrão *Registry* no script `executar_ingestao.py`. A lógica de ingestão foi desacoplada das configurações, permitindo que novas bases sejam adicionadas apenas via metadados (dicionários), sem alteração no código-fonte dos motores.

---

## Padrões de Arquitetura e Governança (Camada Bronze)

Para garantir a integridade analítica e a governança dos dados, a Camada Bronze segue regras estritas implementadas de forma automatizada via código:

1. **Divisão Lógica:** A Camada Bronze atua em dois estágios físicos no Data Lake:
   - `bronze_raw`: Armazena o dado no formato mais fiel possível à origem, atuando como cofre imutável (com aplicação prévia de Hashing LGPD).
   - `bronze_normalized`: Armazena o dado estruturalmente padronizado e tipado, pronto para ser consumido pelas camadas analíticas.
2. **Padrão de Pastas (Particionamento):** O Data Lake segue estritamente o particionamento temporal padrão Hive no formato: `/{camada}/{sistema}/year=YYYY/month=MM/`.
3. **Convenção de Nomenclatura (Naming Convention):** Todas as colunas na camada `bronze_normalized` são convertidas obrigatoriamente para o padrão `snake_case` (ex: "Nome do Servidor" converte para `nome_do_servidor`).
4. **Metadados Obrigatórios:** Toda tabela processada na camada Normalized recebe a injeção automática das seguintes colunas de auditoria:
   - `source_system`: Sistema de origem do dado (ex: `depro_alocacao`).
   - `ingestion_timestamp`: Data e hora exata do processamento e normalização.
   - `schema_version`: Controle de versão estrutural (ex: `v1`).
   - `hash_cpf`: Identificador anonimizado (quando o dado original contiver pessoa física).

---

## Qualidade e Integridade na Camada Bronze (In-Flight Quality)

Diferente do legado, a confiabilidade agora é garantida durante a extração, antes mesmo do dado tocar o disco, através de quatro pilares:

- **Controle de Tipagem Estrita (Schema Enforcement):** O motor dlt valida o schema da API em tempo real; se a fonte mudar o formato de um campo crítico, o pipeline alerta a inconsistência.
- **Anonimização Determinística (LGPD):** Implementação de hashing SHA-256 via `hashlib` para CPFs. O dado sensível é transformado em memória, garantindo que o arquivo físico `.parquet` já nasça em conformidade com a LGPD.
- **Tratamento de Arquivos Corrompidos:** O motor Polars valida a integridade de arquivos `.zip` e `.csv`, abortando a operação em caso de `BadZipFile` para evitar a poluição do Data Lake com lixo digital.
- **Observabilidade Operacional (Dual Logging):** Registro de saúde da ingestão em tempo real (Terminal + Arquivo `.log`), capturando latência, volume de linhas e erros de rede (HTTP 4xx/5xx).

---

## Roadmap Arquitetural

Para garantir a maturidade progressiva da solução (escalabilidade, DataOps e FinOps), o planejamento de evolução das próximas fases (Orquestração com Dagster, CI/CD, Lakehouse) está formalmente registrado.

[Acesse o Roadmap Arquitetural detalhado aqui](docs/ROADMAP_ARQUITETURAL.md)

---

## Status do Projeto

| Fase | Descrição | Status | Entregáveis |
|------|------------|--------|------------|
| **Fase 0** | Base Técnica (Polars + dlt + Parquet + Normalização) | **Concluída** | Estrutura Raw/Normalized, Naming Convention e injeção de Metadados Universais. |
| **Fase 1** | Registry + Orquestrador (Expansão da ingestão) | **Em Execução** | Ingestão das bases estruturantes (SIGEPE, DEPRO, Vozes, Observatório). |
| **Fase 2** | Estabilização da Ingestão | Planejado | Confiabilidade operacional antes de ir para a nuvem. |
| **Fase 3** | Orquestração de Pipelines | Planejado | Automatizar execução e gerenciar dependências com Dagster. |

---

## Tecnologias Utilizadas

- **Linguagem:** Python 3.12 LTS.
- **Processamento Big Data:** Polars, DuckDB, Apache Arrow.
- **Ingestão de APIs:** dlt (Data Load Tool), Requests.
- **Segurança e Governança:** Hashlib (SHA-256), Logging Nativo.
- **Transformação e Qualidade:** dbt Core (Data Build Tool).
- **Armazenamento:** Google BigQuery, Cloud Storage (Formato Parquet).

---

## Como Executar (Pipeline de Ingestão)

### 1. Preparação do Ambiente
Certifique-se de estar com o Python 3.12+ ativo e as dependências instaladas:
```bash
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuração de Credenciais e Variáveis
O projeto utiliza um arquivo `.env` (não versionado) para chaves sensíveis. Crie um na raiz:
```bash
HASH_SALT="sua_chave_de_anonimizacao_aqui"
CHAVE_SIGEPE="seu_token_api_siape_consultas"
CHAVE_SOUGOV="seu_token_api_sougov"
```

### 3. Orquestração da Carga (Padrão Registry)
Para rodar a ingestão das bases mapeadas, utilizamos o orquestrador central que gerencia os motores Polars e dlt:
```bash
python fase3_upgrade_ingestao/executar_ingestao.py
```

## Estrutura do Repositório
```bash
/
├── docs/
│   ├── adrs/                    # Registros de Decisões Arquiteturais (ADR-001 a 006).
│   ├── dicionarios/             # Mapeamento de variáveis das fontes federais.
│   └── homologacoes/            # Termos de aceite da Camada Bronze.
├── fase3_upgrade_ingestao/      # O CORAÇÃO DO PROJETO (Motores + Orquestrador).
│   ├── executar_ingestao.py     # Script central de execução (Orquestrador).
│   ├── pipeline_bronze_raw_api.py       # Motor de extração via dlt.
│   ├── pipeline_bronze_raw_polars.py    # Motor de extração via Polars.
│   └── pipeline_bronze_normalized.py    # Motor de padronização estrutural e metadados.
├── logs/                        # Centralização do Dual Logging de auditoria da Camada Bronze.
├── legado_pandas/               # Scripts arquivados das Fases 1 e 2 originais.
├── data_lake_local/             # Destino físico dos arquivos Parquet particionados.
├── .env.example                 # Modelo de variáveis de ambiente.
├── .gitignore                   # Proteção de logs, venv e pycache.
└── README.md
```

#### Ediney Magalhães
##### Analytics Engineer | Data Engineer | Estatístico