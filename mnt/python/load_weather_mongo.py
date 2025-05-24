from pyspark.sql import SparkSession
from dotenv import load_dotenv
import os
import logging

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
    def __init__(self, mongo_uri=None, database="clima", collection="dados"):
        self.mongo_uri = mongo_uri or os.getenv("MONGO_URI")
        self.database = database
        self.collection = collection

        self.spark = SparkSession.builder \
                    .appName("LoadDataMongoDB") \
                    .config("spark.mongodb.write.connection.uri", self.mongo_uri) \
                    .getOrCreate()

    def ler_parquet(self, caminho_parquet):
        return self.spark.read.parquet(caminho_parquet)

    def escrever_mongodb(self, df):
        df.write \
            .format("mongodb") \
            .mode("append") \
            .option("uri", self.mongo_uri) \
            .option("database", self.database) \
            .option("collection", self.collection) \
            .save()

        self.spark.stop()
        logger.info(f"Dados inseridos no MongoDB -> {self.database}.{self.collection}")
