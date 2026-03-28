# ADR 0009: Estratégia de chave universal (Record Linkage)

**Data:** 28 de Março de 2026
**Status:** Proposto
**Autor:** Ediney Magalhães

## Contexto
O projeto integra bases de origens distintas. Bases do Portal da Transparência entregam `id_servidor_portal` sem CPF real. Bases de APIs restritas entregam CPF real. Sem uma estratégia definida, o JOIN entre essas fontes na Silver retorna zero linhas.

## Decisão
Fazer avaliação das bases após ingestão para definição dos campos que irão compor a chave composta

## Alternativas consideradas
Utilizar chave composta

## Consequências
    * **Positivas:** Única chave para cruzamento das bases e tabelas ingeridas
