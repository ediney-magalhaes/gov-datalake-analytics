# ADR-014: Google Cloud Storage como storage da camada Bronze

**Data:** 18 de Abril de 2026
**Status:** Aceito
**Autor:** Ediney Magalhães

## Contexto
O projeto necessita de um destino de storage para os arquivos Parquet da camada Bronze (Raw e Normalized). O storage precisa atender à premissa de custo zero ou mínimo, ser acessível remotamente, suportar o padrão Hive Partitioning e ser compatível com o BigQuery para a estratégia de External Tables da Fase 4.1.
O hardware local (220 GB de disco, 13,9 GB livres) é insuficiente para armazenar o histórico completo de 10 anos de 6 sistemas — estimado em ~38 GB após compressão Parquet.

## Decisão
Adotar o Google Cloud Storage (GCS) como destino oficial dos arquivos Parquet da camada Bronze Raw e Bronze Normalized.
Configuração adotada:
- Classe de storage: Standard (acesso frequente durante ingestão)
- Região: us-central1 (elegível para Always Free tier)
- Custo estimado: ~US$ 0,60/mês (~R$ 3,00) para ~23 GB
- Organização: bronze_raw/ e bronze_normalized/ com Hive Partitioning (/sistema/year=YYYY/month=MM/)

## Alternativas consideradas
- **Filesystem local:** Rejeitado para produção. Hardware insuficiente (13,9 GB livres) para o volume estimado do histórico completo. Mantido apenas para desenvolvimento 
  e testes locais durante a Fase 1.

- **Amazon S3:** Rejeitado. Introduz dependência de segundo provedor cloud (AWS) sem benefício adicional. A integração nativa GCS + BigQuery + Dagster justifica manter tudo no 
  ecossistema Google Cloud.

- **OneDrive / Google Drive:** Rejeitado. Não suportam acesso programático eficiente via Python para leitura de Parquet particionado. Sem integração nativa com BigQuery.

## Consequências
**Positivas:**
- Custo ~R$ 3,00/mês — compatível com a premissa de custo mínimo do projeto
- Integração nativa com BigQuery via External Tables (Fase 4.1) eliminando duplicação de storage entre Lake e DW
- Libera o disco local para desenvolvimento sem acumular gigabytes de dados históricos
- Dados acessíveis remotamente por múltiplos colaboradores
- Compatível com Hive Partitioning para Partition Pruning

**Negativas / Trade-offs:**
- Custo mensal não é literalmente zero — requer cartão de crédito cadastrado no GCP com alerta de budget configurado
- Dependência de conectividade para ingestão e leitura
- Migração necessária: os arquivos atualmente em data_lake_local/ precisam ser movidos para o GCS

**Ação obrigatória antes da Fase 2:**
Configurar alerta de budget no GCP para US$ 5,00/mês para garantir que nenhum custo inesperado passe despercebido.