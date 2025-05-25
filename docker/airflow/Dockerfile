# Usar imagem oficial do Apache Airflow com Python 3.8
FROM apache/airflow:2.3.0-python3.8

USER root

# Instalar Java (necessário para o Spark)
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk curl && \
    apt-get clean

# Definir variável de ambiente do Java
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Instalar Apache Spark
ENV SPARK_VERSION=3.5.1 \
    HADOOP_VERSION=3

RUN curl -fsSL https://downloads.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    | tar -xz -C /opt/ && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark

ENV SPARK_HOME=/opt/spark
ENV PATH="${SPARK_HOME}/bin:$PATH"

# Instalar PySpark + dependências do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Variáveis de ambiente do PySpark
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Copiar scripts e DAGs
COPY mnt/python /opt/airflow/python
COPY mnt/airflow/dags /opt/airflow/dags
COPY .env /opt/airflow/.env

# Corrigir permissões para o usuário airflow
RUN chown -R airflow:airflow /opt/airflow

USER airflow
