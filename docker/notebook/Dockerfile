FROM python:3.8-slim

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    curl \
    git \
    && apt-get clean

# Variáveis de ambiente do Java/Spark
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Instalar Jupyter e bibliotecas Python
COPY docker/notebook/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Criar pasta de trabalho
WORKDIR /home/jovyan

# Expor a porta padrão do Jupyter
EXPOSE 8888

# Entrypoint
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
