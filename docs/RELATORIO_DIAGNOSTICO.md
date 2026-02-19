# 📊 Relatório Diagnóstico e Mapeamento de Dados (Produto 1)

**Projeto:** Data Lake - Gestão de Pessoal (Governo Federal)
**Objetivo:** Mapeamento estrutural, diagnóstico de qualidade e plano de mitigação de riscos (LGPD) das bases de dados fontes do Poder Executivo Federal.

---

## 1. Mapeamento Estrutural das Bases (As-Is)

Após a etapa de descoberta (Data Discovery) e testes de ingestão, as três bases oficiais foram mapeadas com as seguintes características técnicas:

| Base de Dados | Frequência | Formato Origem | Codificação | Separador | Volume Médio |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SIAPE (Ativos)** | Mensal | `.zip` > `.csv` | `latin1` | `;` | ~700 mil / mês |
| **ENAP (Capacitação)** | Mensal | `.tar.gz` > `.gzip` | `utf-8` | `|` (Pipe) | ~330 mil / mês |
| **SIAPE (Aposentados)** | Mensal | `.zip` > `.csv` | `latin1` | `;` | ~410 mil / mês |

---

## 2. Diagnóstico de Qualidade e Desafios de Ingestão

Durante o desenvolvimento da Camada Bronze, identificamos inconsistências estruturais na origem que exigiram tratamentos avançados no pipeline:

* **Falta de Padronização de Formatos:** O governo disponibiliza bases em formatos de compactação diferentes (`.zip` vs `.tar.gz`) e com delimitadores textuais distintos (ponto e vírgula vs pipe). 
* **Arquivos Massivos Ocultos:** A base da ENAP possui um nível duplo de compactação não documentado (um arquivo `.gzip` escondido dentro do `.tar.gz`), exigindo a biblioteca `tarfile` extraindo dados diretamente na memória RAM (`io.BytesIO`).
* **Risco de Gargalo de Memória (OOM):** A volumetria combinada ultrapassa 1.4 milhão de linhas processadas a cada mês iterado. O pipeline foi desenhado com destruição de instâncias (`del df_mes`) a cada loop para preservar a saúde do servidor.

---

## 3. Matriz de Conformidade LGPD e Anonimização

O tratamento de dados pessoais sensíveis (Lei nº 13.709/2018) varia drasticamente entre as fontes, exigindo uma política de pseudonimização centralizada no pipeline:

* **Bases SIAPE (Ativos e Aposentados):** Os dados são disponibilizados em texto claro. O CPF é mascarado **em tempo real de voo** (*in-flight*) através da biblioteca `hashlib`, aplicando a criptografia unidirecional `SHA-256` antes da persistência no Google BigQuery.
* **Base ENAP:** O CPF já é disponibilizado parcialmente anonimizado na origem (Hash `MD5`). Para garantir a interoperabilidade e cruzamento futuro (JOIN) na Camada Ouro, o robô aplica o `SHA-256` sobre o MD5 existente, garantindo a mesma assinatura criptográfica em todo o Data Lake.

---

> ⚖️ **Trade-off Arquitetural:** Optou-se por hashing determinístico (`SHA-256`) sem uso de salt para preservar capacidade de JOIN entre bases heterogêneas. A decisão prioriza interoperabilidade analítica, mantendo conformidade com LGPD via pseudonimização irreversível.

---
**Status Final:** Diagnóstico Concluído. Pipeline de Ingestão da Camada Bronze adaptado para mitigar 100% das inconsistências mapeadas.