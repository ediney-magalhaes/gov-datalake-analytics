# ADR-001 — Processamento in-memory com Polars para ingestão massiva

**Data:** 2026-02-25  

**Status:** Aceito  

**Decisores:** Ediney Magalhães (Analytics Engineering / Data Engineer)



## Contexto

A ingestão de bases massivas do governo (CSV/ZIP/TAR.GZ) apresentou risco de:

- **OOM** (estouro de memória) com Pandas

- baixa eficiência em parsing e transformação

- aumento de tempo total de carga



## Decisão

Substituir Pandas por **Polars (Apache Arrow)** como motor principal de processamento in-memory.



## Alternativas consideradas

- **Pandas + chunking manual:** aumenta complexidade e risco de bugs; ainda pode estourar memória dependendo do fluxo.

- **PySpark:** exige infraestrutura/cluster; eleva custo e complexidade para um projeto que prioriza leveza.

- **Dask:** melhora paralelismo, mas ainda mantém parte do overhead Python.



## Consequências

Benefícios:

- processamento vetorizado e mais eficiente

- menor risco de OOM

- melhor performance para CSVs grandes



Trade-offs:

- necessidade de adaptar padrões de transformação do Pandas para Polars

- curva curta de aprendizado e diferenças de API



Riscos:

- algumas operações específicas podem exigir conversões para Arrow/Pandas em casos raros



## Validação

- comparar tempo de ingestão e consumo de RAM antes/depois

- logs com throughput e tempo por etapa

- stress tests com base de remuneração



---