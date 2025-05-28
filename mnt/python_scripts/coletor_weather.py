"""
Módulo de coleta de dados climáticos da API OpenWeather.

Este script define a classe `ColetorWeather`, responsável por:
- Coletar dados meteorológicos atuais para uma lista de cidades.
- Salvar os dados coletados em arquivos JSON organizados por ano, mês, dia e hora.
"""

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

class ColetorWeather:
    """
    Classe responsável por coletar dados meteorológicos da API OpenWeather
    e armazená-los em arquivos JSON organizados por data/hora.

    Attributes:
        cidades (list): Lista de nomes de cidades para coleta dos dados.
        api_key (str): Chave da API OpenWeather.
        base_url (str): URL base da API.
        base_path (str): Caminho base para salvar os arquivos JSON.
    """

    def __init__(self, cidades, API_KEY):
        """
        Inicializa o ColetorWeather com a lista de cidades.

        Args:
            cidades (list): Lista com os nomes das cidades (ex: ['São Paulo', 'Rio de Janeiro']).
        """
        self.cidades = cidades
        self.api_key = API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
        )

    def coletar(self):
        """
        Realiza a coleta de dados meteorológicos para todas as cidades definidas.

        Returns:
            list: Lista de dicionários JSON com os dados retornados pela API.
        """
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
        """
        Salva os dados coletados em arquivos JSON organizados por data/hora.

        Args:
            dados (list): Lista de dicionários contendo os dados das cidades.

        Returns:
            str: Caminho completo da pasta onde os arquivos foram salvos.
        """
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
