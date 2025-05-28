"""
DAG do Apache Airflow para pipeline ETL do clima via OpenWeather API.

Esta DAG realiza:
- Extração de dados meteorológicos de diversas cidades brasileiras via API.
- Transformação dos dados brutos com PySpark.
- Carga dos dados transformados no MongoDB.
"""

import os
import sys
from dotenv import load_dotenv

# Adiciona o caminho do diretório de scripts Python dentro do container Airflow
sys.path.append('/opt/airflow/python_scripts')

from coletor_weather import ColetorWeather
from transformador_weather import TransformadorClima
from load_weather_mongo import LoadMongo

from airflow import DAG
from airflow.decorators import task
from datetime import datetime

# Carrega variáveis de ambiente
load_dotenv()

# Configuração padrão da DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
}

with DAG(
    dag_id='pipeline_etl_weather_api',
    default_args=default_args,
    description='Pipeline de extração, transformação e carga de dados do clima para o MongoDB',
    schedule_interval='@hourly',
    start_date=datetime(2025, 5, 24),
    catchup=False,
    tags=['clima', 'ETL', 'MongoDB', 'API'],
) as dag:

    @task
    def extract():
        """
        Etapa de extração dos dados de clima via API OpenWeather.

        Retorna:
            str: Caminho para a pasta onde os arquivos JSON foram salvos.
        """
        cidades = [
            'Rio Branco,BR', 'Maceió,BR', 'Macapá,BR', 'Manaus,BR', 'Salvador,BR',
            'Fortaleza,BR', 'Brasília,BR', 'Vitória,BR', 'Goiânia,BR', 'São Luís,BR',
            'Cuiabá,BR', 'Campo Grande,BR', 'Belo Horizonte,BR', 'Belém,BR', 'João Pessoa,BR',
            'Curitiba,BR', 'Recife,BR', 'Teresina,BR', 'Rio de Janeiro,BR', 'Natal,BR',
            'Porto Alegre,BR', 'Porto Velho,BR', 'Boa Vista,BR', 'Florianópolis,BR',
            'São Paulo,BR', 'Aracaju,BR', 'Palmas,BR'
        ]
        API_KEY = os.getenv("API_KEY")
        coletor = ColetorWeather(cidades, API_KEY)
        dados = coletor.coletar()
        data_path = coletor.salvar_jsons(dados)
        return data_path

    @task
    def transform(data_path: str):
        """
        Etapa de transformação dos dados brutos para formato estruturado.

        Args:
            data_path (str): Caminho dos arquivos JSON extraídos.

        Retorna:
            str: Caminho do diretório com os arquivos Parquet processados.
        """
        transformador = TransformadorClima()
        df_raw = transformador.ler_json(data_path)
        df_transformado = transformador.transformar(df_raw)
        parquet_path = transformador.salvar_parquet(df_transformado)
        return parquet_path

    @task
    def load_data_to_mongo(parquet_path: str):
        """
        Etapa de carga dos dados transformados no MongoDB.

        Args:
            parquet_path (str): Caminho do diretório com arquivos Parquet.
        """
        MONGO_URI = os.getenv("MONGO_URI")
        DATABASE = "clima"
        COLLECTION = "dados"

        mongo_loader = LoadMongo(MONGO_URI, DATABASE, COLLECTION)
        df = mongo_loader.ler_parquet(parquet_path)
        mongo_loader.escrever_mongodb(df)
        mongo_loader.stop()

    # Definição da ordem das tarefas (TaskFlow API)
    data_path = extract()
    parquet_path = transform(data_path)
    load_data_to_mongo(parquet_path)
