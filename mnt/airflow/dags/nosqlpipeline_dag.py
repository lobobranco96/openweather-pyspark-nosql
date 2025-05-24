import os
from dotenv import load_dotenv

from mnt.python.coletor_weather import ColetorWeather
from mnt.python.transformador_weather import TransformadorClima
from mnt.python.load_weather_mongo import LoadMongo

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

load_dotenv() 

def extract(**kwargs):
    cidades = [
        'Rio Branco,BR', 'Maceió,BR', 'Macapá,BR', 'Manaus,BR', 'Salvador,BR',
        'Fortaleza,BR', 'Brasília,BR', 'Vitória,BR', 'Goiânia,BR', 'São Luís,BR',
        'Cuiabá,BR', 'Campo Grande,BR', 'Belo Horizonte,BR', 'Belém,BR', 'João Pessoa,BR',
        'Curitiba,BR', 'Recife,BR', 'Teresina,BR', 'Rio de Janeiro,BR', 'Natal,BR',
        'Porto Alegre,BR', 'Porto Velho,BR', 'Boa Vista,BR', 'Florianópolis,BR',
        'São Paulo,BR', 'Aracaju,BR', 'Palmas,BR'
    ]

    extract = ColetorWeather(cidades)
    dados = extract.coletar()

    data_path = extract.salvar_jsons(dados)  # Salva os arquivos e retorna o caminho

    # Utilizando XCom para passar o caminho para a próxima tarefa
    kwargs['ti'].xcom_push(key='data_path', value=data_path)

def transform(**kwargs):
    # Obter o caminho da tarefa anterior usando XCom
    ti = kwargs['ti']
    data_path = ti.xcom_pull(task_ids='extract_task', key='data_path')

    transformador = TransformadorClima()

    df_raw = transformador.ler_json(data_path)
    df_transformado = transformador.transformar(df_raw)
    parquet_path = transformador.salvar_parquet(df_transformado)  # Salva os dados Parquet

    # Passando o caminho do arquivo Parquet para a próxima tarefa via XCom
    kwargs['ti'].xcom_push(key='parquet_path', value=parquet_path)

def load_data_to_mongo(**kwargs):
      # Obter o caminho do arquivo Parquet da tarefa anterior usando XCom
    ti = kwargs['ti']
    parquet_path = ti.xcom_pull(task_ids='transform_task', key='parquet_path')

    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE = "clima"
    COLLECTION = "dados"

    mongo_loader = LoadMongo(MONGO_URI, DATABASE, COLLECTION)
    
    # Lê o arquivo Parquet
    df = mongo_loader.ler_parquet(parquet_path)
    
    # Escreve os dados no MongoDB
    mongo_loader.escrever_mongodb(df)
    
    # Finaliza a conexão
    mongo_loader.stop()

# Definição do DAG
with DAG(
    'load_weather_data',
    default_args={
        'owner': 'airflow',
        'retries': 1,
    },
    description='Pipeline de extração, transformação e carga de dados do clima para o MongoDB',
    schedule_interval='@hourly',  # Executar a cada hora
    start_date=datetime(2025, 5, 24),
    catchup=False,
) as dag:

    # Tarefa de extração
    extract_task = PythonOperator(
        task_id='extract_task',
        python_callable=extract
    )

    # Tarefa de transformação
    transform_task = PythonOperator(
        task_id='transform_task',
        python_callable=transform,
    )

    # Tarefa de carga no MongoDB
    load_task = PythonOperator(
        task_id='load_data_to_mongo',
        python_callable=load_data_to_mongo,
    )

    # Definir a sequência de execução das tarefas
    extract_task >> transform_task >> load_task
