FROM python:3.9-slim

# Cria a pasta de trabalho
WORKDIR /app

# Instala a biblioteca que vamos usar
RUN pip install pandas sqlalchemy psycopg2-binary

# Copia APENAS o script. O CSV vai entrar depois "por mágica" (Volume)
COPY main.py .

# Comando de execução
CMD ["python", "main.py"]