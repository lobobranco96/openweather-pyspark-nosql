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

# Carregar variáveis de ambiente
load_dotenv()

class LoadMongo:
    def __init__(self, mongo_uri, database, collection):
        self.mongo_uri = mongo_uri
        self.database = database
        self.collection = collection

        # Inicia a sessão do Spark
        self.spark = SparkSession.builder \
                    .appName("LoadDataMongoDB") \
                    .getOrCreate()

        # Conecta ao MongoDB
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.database]
        self.collection_mongo = self.db[self.collection]

    def ler_parquet(self, caminho_parquet):
        """
        Lê o arquivo Parquet com PySpark
        """
        logger.info(f"Lendo arquivo Parquet de {caminho_parquet}")
        return self.spark.read.parquet(caminho_parquet)

    def escrever_mongodb(self, df):
        """
        Converte DataFrame PySpark para pandas e insere no MongoDB com pymongo
        """
        logger.info("Convertendo DataFrame PySpark para Pandas...")
        
        # Converte PySpark DataFrame para Pandas
        df_pandas = df.toPandas()

        # Inserir no MongoDB
        data = df_pandas.to_dict(orient="records")  # converte para lista de dicionários
        if data:
            self.collection_mongo.insert_many(data)
            logger.info(f"Dados inseridos no MongoDB -> {self.database}.{self.collection}")
        else:
            logger.warning(f"Nenhum dado encontrado para inserir no MongoDB.")

    def stop(self):
        """
        Fecha a conexão do Spark e do MongoDB
        """
        logger.info("Finalizando a sessão do Spark e a conexão MongoDB...")
        self.spark.stop()
        self.client.close()
        logger.info("Conexões encerradas.")

