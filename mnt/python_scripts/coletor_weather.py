import requests
import json
from datetime import datetime
from urllib.parse import quote
import os
from dotenv import load_dotenv
import logging

# Configura logging básico
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
# Carrega variáveis do .env
load_dotenv()
API_KEY = os.getenv("API_KEY")

class ColetorWeather:
    def __init__(self, cidades):
        self.cidades = cidades
        self.api_key = API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # Define pasta base absoluta (2 níveis acima + /data/raw)
        self.base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
        )

    def coletar(self):
        resultados = []
        for cidade in self.cidades:
            cidade_encoded = quote(cidade)
            url = f"{self.base_url}?q={cidade_encoded}&appid={self.api_key}&units=metric&lang=pt"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    dados = response.json()
                    resultados.append(dados)
                    logger.info(f"Coletado: {cidade}")
                else:
                    logger.warning(f"Falha em {cidade}: {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"Erro em {cidade}: {e}")
        logger.info(f"Total de cidades coletadas: {len(resultados)}")
        return resultados

    def salvar_jsons(self, dados):
        now = datetime.now()
        pasta_base = os.path.join(
            self.base_path,
            f"ano={now.year}",
            f"mes={now.month:02d}",
            f"dia={now.day:02d}",
            f"hora={now.hour:02d}"
        )
        os.makedirs(pasta_base, exist_ok=True)

        for dado in dados:
            cidade = dado.get('name', 'desconhecida').replace(" ", "_")
            timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
            nome_arquivo = f"clima_{cidade}_{timestamp}.json"
            caminho_completo = os.path.join(pasta_base, nome_arquivo)

            with open(caminho_completo, 'w', encoding='utf-8') as f:
                json.dump(dado, f, ensure_ascii=False, indent=4)

        logger.info(f"Arquivos salvos em: {pasta_base}")
        return pasta_base