# Imagem da aplicação: API FastAPI + página de busca.

# 1. Imagem base: Python 3.13 (o mesmo do .venv) na variante slim.
#    Nome completo porque o Podman não completa nomes curtos sozinho.
FROM docker.io/library/python:3.13-slim

# 2. Faz print() e logs aparecerem na hora, sem ficar presos no buffer.
ENV PYTHONUNBUFFERED=1

# 3. Pasta de trabalho dentro da imagem. Não é /app para o pacote
#    não ficar em /app/app.
WORKDIR /code

# 4. Dependências primeiro. Cada instrução vira uma camada guardada em
#    cache; esta só é refeita quando o requirements.txt muda.
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Código e dados por último: mudar um .py não reinstala as bibliotecas.
COPY app/ app/
COPY data/ data/

# 6. Documenta a porta da API. Quem publica de fato é o compose.
EXPOSE 8000

# 7. Comando que sobe quando o container inicia. --host 0.0.0.0 faz o
#    uvicorn escutar em todas as interfaces do container, e não só no
#    loopback, que só é alcançável de dentro dele.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
