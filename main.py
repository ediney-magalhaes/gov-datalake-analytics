import pandas as pd
import os

ARQUIVO_ENTRADA = '/data/dados.csv'
ARQUIVO_SAIDA = '/data/relatorio_final.csv'

print('--- INICIANDO PROCESSAMENTO ETL ---')

# 1. EXTRACT (Extração)
# Verifica se o arquivo existe antes de tentar ler
if not os.path.exists(ARQUIVO_ENTRADA):
    print(f'ERRO CRÍTICO: Não encontrei o arquivo em {ARQUIVO_ENTRADA}')
    print(f'Dica: Verifique se o Volume do Docker foi montado corretamente.')
    exit(1)

print(f"Lendo arquivo: {ARQUIVO_ENTRADA}...")
df = pd.read_csv(ARQUIVO_ENTRADA)

# 2. TRANSFORM (Transformação)
# Vamos calcular o Custo Médio Diário (evitando divisão por zero)
print("Aplicando regras de negócio...")
df['custo_medio_diario'] = df['custo_internacao'] / (df['dias_uti'].replace(0, 1))
df['custo_medio_diario'] = df['custo_medio_diario'].round(2)

# 3. LOAD (Carga)
print(f"Salvando resultados em: {ARQUIVO_SAIDA}...")
df.to_csv(ARQUIVO_SAIDA, index=False)

print("--- SUCESSO! ETL FINALIZADO ---")