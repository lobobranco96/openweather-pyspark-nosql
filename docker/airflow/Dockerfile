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


USER airflow

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

