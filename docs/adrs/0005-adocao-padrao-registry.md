# ADR-005: Adoção do Padrão Registry para Orquestração da Camada Bronze

* **Data:** 07 de Março de 2026
* **Status:** Aceito

## 1. Contexto
Durante a Fase 1 (Expansão da Camada Bronze), identificamos a necessidade de ingerir múltiplas fontes de dados (APIs como SIGEPE e arquivos como Pesquisa Vozes). A abordagem de criar um script Python individual para cada nova base geraria duplicação de lógica e dificultaria a manutenção do código.

## 2. Decisão
Decidimos implementar o padrão **Configuration Registry**:
* Os motores de ingestão (`pipeline_bronze_raw_api.py` e `pipeline_bronze_raw_polars.py`) permanecem como funções genéricas e puras.
* Criamos um orquestrador central (`executar_ingestao.py`) que armazena os parâmetros das bases em listas de dicionários.
* O orquestrador importa as funções e as executa em loops, passando os parâmetros dinamicamente.

## 3. Consequências
* **Positivas:** Centralização da configuração e facilidade para escalar a ingestão de novas bases sem escrever novo código lógico.
* **Negativas:** Dependência direta da integridade das chaves no arquivo `.env` para o funcionamento das chamadas de API.