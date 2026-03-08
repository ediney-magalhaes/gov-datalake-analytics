# ADR-006: Postergação da Extração de Dados Não-Estruturados (PDFs)

* **Data:** 07 de Março de 2026
* **Status:** Aceito

## 1. Contexto
A "Pesquisa Vozes" é fundamental para cruzar dados de percepção (engajamento/liderança) com dados administrativos do SIAPE. Contudo, identificamos que os microdados brutos não estão disponíveis em formatos estruturados, apenas em relatórios PDF. Nossos motores atuais não possuem lógica de parsing para PDF.

## 2. Decisão
Decidimos isolar a ingestão da Pesquisa Vozes nesta etapa. O foco da Fase 1 será a consolidação de todas as bases estruturadas (CSV, Excel e APIs). A extração de tabelas de PDFs será tratada posteriormente através de um novo motor específico a ser desenvolvido (ex: usando `pdfplumber` ou `camelot`).

## 3. Consequências
* **Positivas:** Mantém o cronograma da Fase 1 focado na estabilização do Data Lake com fontes estruturadas.
* **Negativas:** As análises qualitativas de People Analytics previstas nos editais ficarão pendentes desta extração técnica.