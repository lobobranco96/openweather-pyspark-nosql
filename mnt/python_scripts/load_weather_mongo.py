"""
Módulo de carga de dados transformados no MongoDB.

Este script define a classe `LoadMongo`, responsável por:
- Ler arquivos Parquet com PySpark.
- Converter os dados para pandas.
- Inserir os dados em uma coleção MongoDB usando PyMongo.
"""

from pyspark.sql import SparkSession
from dotenv import load_dotenv
import os
import logging
import pymongo
import pandas as pd

# Configura logging básico
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente do .env
load_dotenv()


class LoadMongo:
    """
    Classe responsável por realizar a carga de dados transformados no MongoDB.

    Funcionalidades:
    - Leitura de arquivos Parquet usando PySpark.
    - Conversão do DataFrame Spark para pandas.
    - Inserção dos dados em uma coleção MongoDB via PyMongo.

    Attributes:
        mongo_uri (str): URI de conexão com o MongoDB.
        database (str): Nome do banco de dados MongoDB.
        collection (str): Nome da coleção MongoDB.
        spark (SparkSession): Sessão ativa do PySpark.
        client (MongoClient): Cliente PyMongo conectado.
        db (Database): Banco de dados MongoDB.
        collection_mongo (Collection): Objeto da coleção MongoDB.
    """

    def __init__(self, mongo_uri, database, collection):
        """
        Inicializa a sessão Spark e conecta ao MongoDB.

        Args:
            mongo_uri (str): URI de conexão MongoDB.
            database (str): Nome do banco de dados.
            collection (str): Nome da coleção.
        """
        self.mongo_uri = mongo_uri
        self.database = database
        self.collection = collection

        self.spark = SparkSession.builder \
            .appName("LoadDataMongoDB") \
            .getOrCreate()

        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.database]
        self.collection_mongo = self.db[self.collection]

    def ler_parquet(self, caminho_parquet):
        """
        Lê arquivos Parquet com PySpark.

        Args:
            caminho_parquet (str): Caminho para os arquivos Parquet.

        Returns:
            DataFrame: DataFrame Spark com os dados lidos.
        """
        logger.info(f"Lendo arquivo Parquet de {caminho_parquet}")
        return self.spark.read.parquet(caminho_parquet)

    def escrever_mongodb(self, df):
        """
        Insere dados no MongoDB após converter de PySpark para pandas.

        Args:
            df (DataFrame): DataFrame Spark a ser inserido no MongoDB.
        """
        logger.info("Convertendo DataFrame PySpark para Pandas...")

        df_pandas = df.toPandas()
        data = df_pandas.to_dict(orient="records")

        if data:
            self.collection_mongo.insert_many(data)
            logger.info(f"Dados inseridos no MongoDB -> {self.database}.{self.collection}")
        else:
            logger.warning("Nenhum dado encontrado para inserir no MongoDB.")

    def stop(self):
        """
        Encerra a sessão do Spark e fecha a conexão com o MongoDB.
        """
        logger.info("Finalizando a sessão do Spark e a conexão MongoDB...")
        self.spark.stop()
        self.client.close()
        logger.info("Conexões encerradas.")
