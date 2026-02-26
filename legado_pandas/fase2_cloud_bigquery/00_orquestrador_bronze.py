import subprocess
import logging
import time

# Configurando o log central
logging.basicConfig(filename='auditoria_bronze.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# A lista de robôs na ordem exata que devem ser executados
scripts_bronze = [
    'fase_2/11_ingestao_siape_bronze.py',
    'fase_2/12_ingestao_enap_bronze.py',
    'fase_2/13_ingestao_aposentados_bronze.py'
]

logging.info("🚀 ======================================================= 🚀")
logging.info("INICIANDO ORQUESTRAÇÃO COMPLETA DA CAMADA BRONZE (FULL LOAD)")
logging.info("🚀 ======================================================= 🚀")

tempo_inicio = time.time()

# O loop que "passa o carro"
for script in scripts_bronze:
    logging.info(f"⏳ Acionando robô: {script}...")
    
    # Executa o script e espera ele terminar
    resultado = subprocess.run(['python', script])
    
    # Se der erro no robô atual, ele quebra o pipeline para não sujar o resto (Fail-Fast)
    if resultado.returncode != 0:
        logging.error(f"❌ Erro crítico no {script}. Orquestração abortada!")
        break
    else:
        logging.info(f"✅ {script} finalizado com sucesso!")

tempo_fim = time.time()
duracao_minutos = (tempo_fim - tempo_inicio) / 60

logging.info("🏁 ======================================================= 🏁")
logging.info(f"ORQUESTRAÇÃO CONCLUÍDA COM SUCESSO EM {duracao_minutos:.2f} MINUTOS")
logging.info("🏁 ======================================================= 🏁")