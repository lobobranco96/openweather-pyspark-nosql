# Open Weather ETL Pipeline

Este projeto realiza a ingestão, transformação e disponibilização de dados meteorológicos obtidos por meio da API da [OpenWeather](https://openweathermap.org/api). O objetivo é construir um pipeline de engenharia de dados completo, orquestrado com Apache Airflow, armazenando os dados em um banco NoSQL (MongoDB) e disponibilizando visualizações interativas via Streamlit.

---

## 📌 Objetivo

> Automatizar a coleta e transformação de dados climáticos por meio de uma pipeline em batch que executa ciclos de ETL a cada hora, garantindo dados atualizados para visualização e análise..

---

## 🧱 Arquitetura

![Arquitetura do Projeto](docs/arquitetura.png)

---

## 🔄 Fluxo de dados

O pipeline segue a abordagem de **ETL (Extract, Transform, Load)**:

1. **Extração**:
   - Os dados climáticos são coletados da OpenWeather API utilizando scripts em Python.
   - Essa etapa é acionada automaticamente pelo **Apache Airflow**, que agenda a execução da DAG a cada `@hour`.

2. **Transformação**:
   - Os dados brutos salvos na pasta `raw/` são tratados, normalizados e enriquecidos com **PySpark**.
   - O resultado da transformação é salvo no diretório `processed/`.

3. **Carga**:
   - Os dados processados são inseridos no banco de dados **MongoDB**, organizados por cidade e data.

4. **Visualização**:
   - Um aplicativo desenvolvido com **Streamlit** consome os dados do MongoDB para gerar dashboards interativos e atualizados automaticamente com cada execução da pipeline.
     
---

## 📅 Agendamento e Orquestração com Airflow

- A orquestração da pipeline é feita utilizando o **Apache Airflow**.
- A DAG principal é executada **automaticamente a cada hora (`@hour`)**, garantindo que o MongoDB e o dashboard estejam sempre atualizados com os dados mais recentes da API.
- Cada execução da DAG é composta por três etapas sequenciais:
  1. `extract_weather_data` – Extrai os dados da OpenWeather API e salva em `raw/`.
  2. `transform_with_pyspark` – Processa os dados com PySpark e salva em `processed/`.
  3. `load_to_mongodb` – Carrega os dados transformados no MongoDB.

---

## ⚙️ Tecnologias Utilizadas

| Tecnologia  | Papel no projeto                         |
|-------------|-------------------------------------------|
| Python      | Scripts de extração e lógica do ETL       |
| Airflow     | Orquestração e agendamento das tarefas    |
| Docker      | Containerização de todos os serviços      |
| PySpark     | Transformação dos dados                   |
| MongoDB     | Banco NoSQL para persistência dos dados   |
| Streamlit   | Interface web para visualização dos dados |
| Jupyter     | Testes e análise exploratória             |

---

## 🐳 Execução com Makefile e Docker

Para iniciar todos os serviços com make:

```bash
up:
	docker compose -f services/orchestration.yml -f services/applications.yml -f services/visualization.yml up -d

down:
	docker compose -f services/orchestration.yml -f services/applications.yml -f services/visualization.yml down

build:
	docker compose -f services/orchestration.yml -f services/applications.yml up -f services/visualization.yml up -d --build

streamlit:
	docker compose -f services/visualization.yml up -d

make up
make down
make build
```

