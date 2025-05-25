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
    def __init__(self):
        self.spark = SparkSession.builder \
                    .appName("TransformadorClima") \
                    .getOrCreate()

        self.base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
        )
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
        """
        Salva o DataFrame transformado como Parquet
        Retorna o caminho onde o arquivo Parquet foi salvo
        """
        now = datetime.now()
        path_base = os.path.join(
            self.base_path,
            f"ano={now.year}",
            f"mes={now.month:02d}",
            f"dia={now.day:02d}",
            f"hora={now.hour:02d}"
        )
        os.makedirs(path_base, exist_ok=True)

        df.write.mode("overwrite").parquet(path_base)
        self.spark.stop()
        logger.info(f"Dados salvos em: {path_base}")
        return path_base
