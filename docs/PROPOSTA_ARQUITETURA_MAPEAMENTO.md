# 🏛️ Documento de Mapeamento de Bases e Arquitetura de Dados

**Projeto:** Data Lake - Gestão de Pessoal (Governo Federal)  
**Responsável Técnico:** Ediney Magalhães - Analytics Engineer  
**Data:** Fevereiro/2026  

---

## 1. Mapeamento das Bases de Dados Existentes

Em atendimento às exigências do edital, foi realizado o levantamento e mapeamento das bases de dados pertencentes à Secretaria de Gestão de Pessoas (SGP) e à Escola Nacional de Administração Pública (ENAP).

| Base de Dados | Origem / Órgão | Estrutura e Formato | Frequência de Atualização | Restrições e Tratamento LGPD |
| :--- | :--- | :--- | :--- | :--- |
| **DW SIAPE** | SGP (Gestão de Pessoas) | Estruturado (Tabelas Relacionais / Arquivos CSV exportados via Portal/API). | Mensal (Fechamento da folha). | **Altíssima.** Contém CPF, remuneração e dados sensíveis. **Tratamento:** Aplicação obrigatória de Hashing (SHA-256) na coluna CPF logo na camada de ingestão. |
| **DATALAKE** | SGP (Gestão de Pessoas) | Semi-estruturado (Arquivos JSON, Parquet, CSV em Storage/Hadoop). | Diária / *Near real-time*. | **Alta.** Acesso restrito (IAM). Dados pessoais mascarados na transição para camadas analíticas. |
| **Base DEPRO** | ENAP (Desenvolvimento Profissional) | Estruturado (Acesso via API JSON ou extração CSV). | Diária ou Semanal. | **Alta.** Contém histórico acadêmico atrelado ao CPF. **Tratamento:** Hashing do CPF para viabilizar o cruzamento (JOIN) com o SIAPE de forma anonimizada. |

---

## 2. Proposta de Arquitetura de Pipelines de Dados (Fluxo ELT)

A arquitetura proposta segue o paradigma moderno de **Medallion Architecture (Arquitetura Medalhão)** em ambiente Cloud Native (Google Cloud Platform), utilizando o modelo **ELT (Extract, Load, Transform)**.

### Fluxo de Dados e Camadas

1. **Origem (Sources):** Extração via APIs governamentais e leitura em memória RAM (`io.BytesIO`), sem persistência de arquivos físicos locais por segurança.
2. **Camada Bronze (Raw):** Ingestão em *Micro-batching* para otimização de memória. Todos os campos entram como texto (`dtype=str`) para evitar falhas de tipagem (*Mixed Types*). Aplicação imediata de Pseudonimização (Hash SHA-256) no CPF. Armazenamento no BigQuery.
3. **Camada Prata (Trusted):** *Data Quality Gate*. Limpeza de nulos irreais (ex: strings vazias `''`), conversão (Cast) de tipos adequados (`DATE`, `FLOAT64`) e deduplicação via SQL parametrizado (dbt ou BigQuery SQL).
4. **Camada Ouro (Refined):** Criação de Tabelas Fato e Dimensão. Cruzamento seguro entre SIAPE (RH) e DEPRO (Cursos) utilizando a chave primária pseudonimizada (`HASH_CPF`). Conexão nativa com ferramentas de BI.

---

## 3. Premissas, Riscos e Decisões Arquiteturais

Para garantir a sustentabilidade, segurança e escalabilidade do Data Lake, o desenho da arquitetura foi fundamentado nas seguintes diretrizes táticas:

### 📌 Premissas Arquiteturais
* Dados pessoais sensíveis (PII) **não devem ser persistidos** em texto claro em nenhuma camada de armazenamento definitivo em nuvem.
* Transformações e limpezas complexas devem ocorrer apenas **após** a persistência do dado bruto na camada controlada (Paradigma ELT).
* A arquitetura deve ser elasticamente escalável para suportar volumes crescentes de dados sem refatoração do código base.
* O pipeline de ingestão deve ser resiliente a falhas temporárias de rede ou indisponibilidade de APIs governamentais.

### ⚠️ Riscos Identificados e Mitigações
* **Mudanças não documentadas no schema das APIs:** Mitigado pelo carregamento inicial na camada Bronze totalmente como *String*, transferindo a quebra de contrato para a camada de transformação (Prata), protegendo a rastreabilidade histórica.
* **Crescimento volumétrico (Out of Memory):** Arquivos contendo milhões de linhas podem estourar a memória do *worker*. Mitigado pela implementação de ingestão por *Micro-batching* e limpeza forçada de RAM (`del DataFrame`).
* **Interrupções temporárias no Endpoint:** O pipeline captura *Status Codes* da web (ex: 404) e registra em logs contínuos, permitindo auditoria sem paralisar as demais cargas programadas.

### ⚖️ Trade-offs (Decisões de Design)
* **ELT vs. ETL Tradicional:** Optou-se pelo ELT (descarregar primeiro, transformar depois) para alavancar o poder de processamento massivo e paralelo (MPP) do Google BigQuery, reduzindo o tempo de máquina da aplicação Python.
* **Micro-batching vs. Processamento em Memória Total:** Abriu-se mão de um código mais curto e de concatenação total (`pd.concat`) em favor de múltiplos *jobs* de *Append*, trocando um leve overhead de rede pela garantia de estabilidade da memória do servidor.
* **Pseudonimização Criptográfica vs. Tabela de De/Para:** Optou-se pelo Hash Determinístico (SHA-256) sem salt aleatório. O trade-off é a impossibilidade técnica de reverter o CPF original, garantindo a LGPD de forma irreversível, mas ganhando a capacidade de realizar *JOINs* exatos com a base da ENAP.

## ⚠️ Matriz de Riscos Técnicos e Mitigação

Como o Data Lake consome dados de fontes externas governamentais, foram mapeados os seguintes riscos e suas respectivas estratégias de mitigação arquitetural:

| Risco Identificado | Nível de Impacto | Estratégia de Mitigação (Contramedida) |
|:---|:---:|:---|
| **1. Indisponibilidade das APIs (Portal da Transparência / ENAP)** | Alto | Implementação de blocos `try/except` nos scripts Python, registro do erro no arquivo `auditoria_bronze.log` e ausência de falha em cascata (o pipeline não trava, apenas reporta a indisponibilidade). |
| **2. Alteração repentina de layout (Mudança de colunas na origem)** | Alto | Processamento agnóstico na Camada Bronze (ingestão "as is"). O bloqueio e alerta de mudança de esquema serão implementados na Fase 3 via testes de Qualidade de Dados (dbt tests) na Camada Prata. |
| **3. Estouro de Memória (OOM - Out of Memory) por alto volume** | Médio | Arquitetura *Cloud Native* utilizando streams em memória (`io.BytesIO`) e extração iterativa (arquivos internos de `.zip` e `.tar.gz` tratados individualmente), eliminando a necessidade de grandes discos locais ou memória RAM massiva. |
| **4. Exposição acidental de PII (Dados Pessoais Sensíveis)** | Altíssimo | O pipeline de ingestão aplica Hash SHA-256 de forma determinística *in-flight* (antes do dado tocar o BigQuery). Os dados chegam na nuvem já pseudonimizados. |

---

## 💻 Requisitos de Infraestrutura e Recursos Necessários

Para a operação plena deste pipeline, a arquitetura exige o seguinte *setup* mínimo, focado em alta escalabilidade e baixo custo (FinOps):

* **Processamento (Computação):**
  * Ambiente de execução Python 3.12+ (Pode ser executado localmente, em VMs básicas, ou via *Cloud Functions*/*Cloud Run* no futuro).
  * Conexão de internet com banda larga para download de arquivos massivos (1GB+).
* **Armazenamento e Data Warehouse (GCP):**
  * Conta ativa no Google Cloud Platform (GCP).
  * API do **Google BigQuery** habilitada.
  * Uso contido dentro do *Free Tier* (10 GB de armazenamento e 1 TB de query/mês gratuitos).
* **Segurança (IAM):**
  * *Service Account* do GCP com permissão de `BigQuery Data Editor` e `BigQuery User`.
  * Chave de acesso `.json` isolada e protegida (ignorada no controle de versão via `.gitignore`).

  ## 🔐 Governança e Otimização de Custos (FinOps) no BigQuery

Para garantir a escalabilidade analítica e o controle rigoroso de custos na nuvem (FinOps), a arquitetura define as seguintes diretrizes para as camadas Prata e Ouro:

### 1. Estratégia de Particionamento e Clustering
O Google BigQuery cobra por volume de dados processados em cada consulta (query). Para mitigar varreduras completas (Full Table Scans):
* **Particionamento (Partitioning):** As tabelas Fato e grandes volumes na Camada Prata serão particionadas por data (ex: `Mês/Ano de Competência` da folha de pagamento do SIAPE). Isso isola os dados fisicamente.
* **Clustering:** O agrupamento de dados será aplicado em colunas de alta cardinalidade e uso frequente em filtros de BI (ex: `Órgão de Lotação` ou `UF do Servidor`), acelerando o tempo de resposta do painel.

### 2. Políticas de Retenção e Versionamento
* **Data Lineage:** A linhagem de dados (Origem → Bronze → Prata → Ouro) será documentada e gerada automaticamente via **dbt docs**, garantindo a rastreabilidade visual do fluxo ETL.
* **Versionamento de Schema:** Mudanças estruturais nos dados serão controladas via repositório Git. As transformações serão tratadas como código (Analytics as Code).
* **Slowly Changing Dimensions (SCD):** O histórico de mudanças de atributos dos servidores (ex: mudança de cargo ou estado) será gerenciado via SCD Tipo 2 na Fase de Modelagem Ouro, utilizando *Snapshots*.