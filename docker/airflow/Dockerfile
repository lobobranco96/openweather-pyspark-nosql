# Usar imagem oficial do Apache Airflow com Python 3.8
FROM apache/airflow:2.3.0-python3.8

USER root

# Instalar Java (necessário para Spark)
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get clean

# Instalar dependências do projeto
COPY docker/airflow/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Criar variáveis de ambiente do Spark
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Copiar os scripts e DAGs
COPY mnt/python /opt/airflow/python
COPY mnt/airflow/dags /opt/airflow/dags
COPY .env /opt/airflow/.env

# Corrigir permissões
RUN chown -R airflow:airflow /opt/airflow

USER airflow
