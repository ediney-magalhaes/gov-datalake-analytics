# 📖 Dicionário de Dados e Mapeamento de Fontes

Este documento detalha as fontes de dados mapeadas para o Data Lake do Governo Federal (Camada Bronze), atendendo aos requisitos de governança e arquitetura do Produto 1.

---

## 1. Portal da Transparência - Servidores (SIAPE)
* **Descrição:** Base central de cadastro e remuneração do executivo federal.
* **Formato de Origem:** Arquivos particionados `.zip` contendo `.csv`.
* **Frequência de Atualização:** Mensal.
* **Método de Ingestão:** Micro-batching em memória (`io.BytesIO`) com chamadas HTTP.
* **Restrições LGPD e Segurança:** * O CPF é considerado dado sensível. Aplicação de criptografia determinística (Hash SHA-256) *in-flight* antes da persistência no Data Lake.
  * Nomes e Cargos são mantidos em texto claro, amparados pela Lei de Acesso à Informação (LAI).

---

## 2. Escola Virtual Gov (ENAP)
* **Descrição:** Base consolidada de matrículas e histórico de capacitação de servidores.
* **Formato de Origem:** Pacote unificado `.tar.gz` contendo arquivos `.csv` compactados em `.gzip`.
* **Frequência de Atualização:** Mensal (Consolidado dos últimos 12 meses).
* **Método de Ingestão:** Extração via API com descompactação dupla em memória RAM. Separador não-padrão (`|`).
* **Restrições LGPD e Segurança:**
  * O CPF já vem pré-mascarado na origem (Hash MD5).
  * Para manter a idempotência do pipeline, aplica-se a mesma função Hash SHA-256 sobre a chave MD5, padronizando a segurança da Camada Bronze.

---

## 3. Servidores Inativos e Pensionistas (SIAPE - Aposentadorias)
* **Fonte:** Portal da Transparência do Governo Federal (API Pública).
* **Frequência de Atualização:** Mensal.
* **Formato de Origem:** Arquivo `.zip` contendo `.csv` (separador `;`, encoding `latin1`).
* **Granularidade:** 1 linha por servidor inativo/pensionista por mês de competência.
* **Volume Médio:** ~410.000 registros por mês (Totalizando ~4.95 milhões de registros anuais).
* **Tratamento LGPD (Bronze):** Coluna `CPF` mascarada via hash determinístico `SHA-256` em tempo real de ingestão (antes do armazenamento no BigQuery).

---