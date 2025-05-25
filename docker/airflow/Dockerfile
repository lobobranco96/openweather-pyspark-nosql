FROM apache/airflow:2.9.1-python3.11

USER root

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y \
    curl \
    git \
    default-jdk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Variáveis de ambiente do Java/Spark
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Variáveis de ambiente do PySpark
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Instalar PySpark + dependências do projeto
COPY requirements.txt .

# Muda para usuário airflow para instalar pacotes
USER airflow

RUN pip install --no-cache-dir -r requirements.txt

#USER root
# Corrigir permissões para o usuário airflow
#RUN chown -R airflow:airflow /opt/airflow

