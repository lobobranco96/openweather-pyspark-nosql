from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_unixtime, when, current_timestamp
import os
from datetime import datetime
import logging

# Configura logging básico
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TransformadorClima:
    def __init__(self, base_path="data/processed"):
        self.base_path = base_path
        self.spark = SparkSession.builder \
                    .appName("TransformadorClima") \
                    .getOrCreate()

    def ler_json(self, caminho_json):
        return self.spark.read.option("multiline", "true").json(caminho_json)

    def transformar(self, df):
        return df.select(
            col("name").alias("cidade"),
            col("dt").alias("timestamp"),
            col("main.temp").alias("temperatura"),
            col("main.humidity").alias("umidade"),
            col("wind.speed").alias("velocidade_vento"),
            col("weather")[0]["description"].alias("descricao_clima")
        ).withColumn(
            "data_hora", from_unixtime(col("timestamp"))
        ).withColumn(
            "faixa_temperatura",
            when(col("temperatura") < 15, "Frio")
            .when(col("temperatura") < 30, "Agradável")
            .otherwise("Quente")
        ).withColumn(
            "data_coleta", current_timestamp()
        ).filter(
            (col("temperatura") > -30) & (col("temperatura") < 50)
        ).na.fill({
            "umidade": 0,
            "velocidade_vento": 0
        })

    def salvar_parquet(self, df):
        now = datetime.now()
        pasta_base = os.path.join(
