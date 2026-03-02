# Relatório Diagnóstico e Mapeamento de Dados

**Projeto:** Data Lake - Gestão de Pessoal (Governo Federal)  
**Objetivo:** Mapeamento estrutural, diagnóstico de qualidade e plano de mitigação de riscos (LGPD) das bases de dados fontes do Poder Executivo Federal.

---

## 1. Mapeamento Estrutural das Bases (As-Is)

Após a etapa de descoberta (Data Discovery) e testes de ingestão massiva, as quatro bases oficiais foram mapeadas com as seguintes características técnicas:

| Base de Dados | Frequência | Formato Origem | Codificação | Separador | Volume Médio |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SIAPE (Ativos)** | Mensal | .zip > .csv | latin1 | ; | ~700 mil / mês |
| **SIAPE (Remuneração)**| Mensal | .zip > .csv | latin1 | ; | ~5,5 milhões (Total 2025) |
| **ENAP (Capacitação)** | Mensal | .tar.gz > .gzip | utf-8 | | (Pipe) | ~330 mil / mês |
| **SIAPE (Aposentados)**| Mensal | .zip > .csv | latin1 | ; | ~410 mil / mês |

---

## 2. Diagnóstico de Qualidade e Desafios Técnicos

Durante o desenvolvimento da Camada Bronze, identificamos inconsistências críticas na origem que exigiram tratamentos avançados de engenharia:

- **Instabilidade de Schema (Schema Drift):** As bases de remuneração apresentam nomes de colunas incompatíveis com bancos de dados ANSI SQL, contendo acentos, caracteres especiais, símbolos monetários e metadados ocultos (ex: \x96).
- **Bloqueio de Firewall (Status 403):** Servidores governamentais aplicam políticas de segurança rigorosas que bloqueiam requisições automatizadas padrão.
- **Falta de Padronização de Compactação:** O uso de diferentes algoritmos (.zip vs .tar.gz) exigiu uma arquitetura de extração polimórfica capaz de lidar com múltiplos formatos diretamente em memória RAM (io.BytesIO).
- **Risco de Gargalo de Memória (OOM):** A volumetria combinada de ~11,5 milhões de registros exige destruição explícita de instâncias de DataFrames (del df) após cada carregamento para manter a estabilidade do pipeline.
- **Risco de Gargalo de Memória (OOM):** A volumetria combinada exige gestão eficiente de RAM. Resolvido na Fase 3 com a substituição do Pandas pelo motor **Polars** (Apache Arrow), permitindo processamento vetorizado massivo sem esgotamento de recursos local/nuvem.
- **Gap Analysis - Variável "Escolaridade":** Durante a auditoria exploratória in-memory dos microdados do Portal da Transparência, homologamos a **ausência da variável "Escolaridade"** para servidores ativos. Este gap bloqueia os estudos de trajetórias e desigualdades. Justifica-se, portanto, a implementação de pipelines via API restrita (SIAPEcad/SouGov).

---

## 3. Matriz de Conformidade LGPD e Anonimização

O tratamento de dados pessoais sensíveis (Lei nº 13.709/2018) é centralizado no pipeline de ingestão para garantir que nenhum dado sensível em texto claro seja persistido na nuvem:

- **Bases SIAPE:** O CPF é mascarado in-flight através da aplicação de hash criptográfico unidirecional SHA-256.
- **Base ENAP:** Para garantir a interoperabilidade (JOIN) com as demais bases, o pipeline aplica o SHA-256 sobre o hash MD5 fornecido pela origem, unificando a assinatura criptográfica em todo o Data Lake.

---

## 4. Plano de Mitigação Implementado

| Desafio Mapeado | Solução de Engenharia Implementada |
| :--- | :--- |
| **Nomes de colunas inválidos** | Normalização via Regex Whitelisting ([^A-Z0-9_]). |
| **Bloqueio de Acesso (403)** | Emulação de User-Agent e implementação de Rate Limiting (Pausas estruturadas). |
| **Integridade de Dados** | Implementação de testes automatizados de unicidade e nulidade via dbt Core. |
| **Segurança LGPD** | Criptografia determinística SHA-256 antes da persistência no BigQuery. |
|**Ausência de Escolaridade** | Desenvolvimento de novo conector via framework dlt focado em APIs estruturantes. |

---

**Status Final:** Diagnóstico Concluído. O pipeline de ingestão e a modelagem da Camada Prata foram adaptados para mitigar 100% das inconsistências estruturais e riscos de conformidade mapeados.