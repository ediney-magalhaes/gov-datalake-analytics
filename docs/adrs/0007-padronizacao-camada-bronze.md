# ADR 0007: Padronização e Governança da Camada Bronze (Raw e Normalized)

**Data:** 14 de Março de 2026
**Status:** Aceito
**Autor:** Ediney Magalhães

## Contexto
O Data Lake lida com dados heterogêneos de diversas fontes do Governo Federal (APIs, CSVs, planilhas). Historicamente, a ingestão salvava os dados "como vieram", o que gerava uma dívida técnica massiva nas camadas analíticas (Silver/Gold), pois os engenheiros de analytics precisavam tratar nomes de colunas inconsistentes (ex: "Nome do Servidor", "NOME", "nome_servidor") e não tinham como auditar a origem exata ou a data de extração de cada linha. Para o escopo do PNUD, a ausência de metadados de auditoria compromete a confiabilidade do estudo.

## Decisão
Fica estabelecida a divisão lógica e física da Camada Bronze em dois estágios sequenciais, com regras estritas de governança aplicadas via código (Motor Polars):

1. **Bronze Raw:** Atua como um cofre de dados imutável. O dado é salvo no formato `.parquet` mantendo a estrutura original da fonte, com a única exceção da aplicação obrigatória de Hashing (SHA-256) na coluna CPF para conformidade com a LGPD (*In-Flight Security*).
2. **Bronze Normalized:** Estágio de padronização estrutural. Todo dado proveniente da `Raw` deve passar por um motor de normalização que aplica obrigatoriamente:
   - **Convenção de Nomenclatura:** Transformação de todos os cabeçalhos para `snake_case` via Regex, eliminando espaços e caracteres especiais.
   - **Injeção de Metadados Universais:** Adição das colunas `source_system` (rastreabilidade da fonte), `ingestion_timestamp` (auditoria de tempo) e `schema_version` (controle de quebras de contrato).
3. **Particionamento Universal:** Ambas as pastas utilizam a estrutura `/year=YYYY/month=MM/`.

## Consequências

**Positivas:**
* **Governança Forte:** Qualquer linha no Data Lake agora pode ser auditada até sua origem exata e momento de ingestão.
* **Facilidade Analítica:** A camada Silver (dbt) receberá dados com colunas padronizadas, reduzindo a complexidade das queries SQL.
* **Conformidade (Compliance):** Atende aos requisitos de auditoria dos editais do projeto governamental.

**Negativas / Trade-offs:**
* **Custo de I/O Dobrado:** O pipeline agora exige ler e escrever no disco duas vezes (uma para a Raw e outra para a Normalized) para o mesmo lote de dados, aumentando levemente o tempo de processamento e o uso do armazenamento temporário. Esse trade-off foi aceito em prol da organização arquitetural.