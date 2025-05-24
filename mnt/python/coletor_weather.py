import requests
import json
from datetime import datetime
from urllib.parse import quote
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()
API_KEY = os.getenv("API_KEY")

class ColetorWeather:
    def __init__(self, cidades):
        self.cidades = cidades
        self.api_key = API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

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
                    print(f"[✓] Coletado: {cidade}")
                else:
                    print(f"[!] Falha em {cidade}: {response.status_code}")
            except Exception as e:
                print(f"[!] Erro em {cidade}: {e}")
        return resultados

    def salvar_jsons(self, dados, pasta='dados_json'):
        for dado in dados:
            cidade = dado.get('name', 'desconhecida').replace(" ", "_")
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            nome_arquivo = f"data/clima_{cidade}_{timestamp}.json"
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dado, f, ensure_ascii=False, indent=4)
