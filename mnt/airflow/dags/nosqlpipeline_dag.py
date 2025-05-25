import os
from dotenv import load_dotenv
import sys

# Adiciona o caminho /opt/airflow/python ao sys.path dentro do container
sys.path.append('/opt/airflow/python_scripts')

from coletor_weather import ColetorWeather
from transformador_weather import TransformadorClima
from load_weather_mongo import LoadMongo

from airflow import DAG
from airflow.decorators import task
from datetime import datetime

load_dotenv()

default_args = {
    'owner': 'airflow',
    'retries': 1,
}

with DAG(
    'pipeline_etl_weather_api',
    default_args=default_args,
    description='Pipeline de extração, transformação e carga de dados do clima para o MongoDB',
    schedule_interval='@hourly',
    start_date=datetime(2025, 5, 24),
    catchup=False,
) as dag:

    @task
    def extract():
        cidades = [
            'Rio Branco,BR', 'Maceió,BR', 'Macapá,BR', 'Manaus,BR', 'Salvador,BR',
            'Fortaleza,BR', 'Brasília,BR', 'Vitória,BR', 'Goiânia,BR', 'São Luís,BR',
            'Cuiabá,BR', 'Campo Grande,BR', 'Belo Horizonte,BR', 'Belém,BR', 'João Pessoa,BR',
            'Curitiba,BR', 'Recife,BR', 'Teresina,BR', 'Rio de Janeiro,BR', 'Natal,BR',
            'Porto Alegre,BR', 'Porto Velho,BR', 'Boa Vista,BR', 'Florianópolis,BR',
            'São Paulo,BR', 'Aracaju,BR', 'Palmas,BR'
        ]

        coletor = ColetorWeather(cidades)
        dados = coletor.coletar()
        data_path = coletor.salvar_jsons(dados)  # Retorna caminho dos arquivos salvos

        return data_path

    @task
    def transform(data_path: str):
        transformador = TransformadorClima()

        df_raw = transformador.ler_json(data_path)
        df_transformado = transformador.transformar(df_raw)
        parquet_path = transformador.salvar_parquet(df_transformado)  # Retorna caminho parquet

        return parquet_path

    @task
    def load_data_to_mongo(parquet_path: str):
        MONGO_URI = os.getenv("MONGO_URI")
        DATABASE = "clima"
        COLLECTION = "dados"

        mongo_loader = LoadMongo(MONGO_URI, DATABASE, COLLECTION)

        df = mongo_loader.ler_parquet(parquet_path)
        mongo_loader.escrever_mongodb(df)
        mongo_loader.stop()

    # tarefas usando a API TaskFlow
    data_path = extract()
    parquet_path = transform(data_path)
    load_data_to_mongo(parquet_path)
