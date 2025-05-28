import streamlit as st
from pymongo import MongoClient
import pandas as pd
import datetime
import os
from dotenv import load_dotenv

load_dotenv()
# Conexão com MongoDB
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["clima"]
collection = db["dados"]
dados = list(collection.find())
df = pd.DataFrame(dados)

# Conversão de datas
df["data_coleta"] = pd.to_datetime(df["data_coleta"])
df["data_hora"] = pd.to_datetime(df["data_hora"])

# Interface com múltiplas abas
aba = st.sidebar.radio("📌 Selecione a aba", [
    "📍 Visão Geral",
    "🌡️ Temperatura por Cidade",
    "💧 Umidade",
    "🌬️ Velocidade do Vento",
    "🌦️ Condição do Clima"
])

# 1. Visão Geral
if aba == "📍 Visão Geral":
    st.title("📍 Visão Geral")
    st.dataframe(df[["cidade", "temperatura", "umidade", "descricao_clima", "data_hora"]])

# 2. Temperatura por Cidade
elif aba == "🌡️ Temperatura por Cidade":
    st.title("🌡️ Temperatura")
    st.bar_chart(df.set_index("cidade")["temperatura"])

# 3. Umidade
elif aba == "💧 Umidade":
    st.title("💧 Umidade")
    st.line_chart(df.set_index("cidade")["umidade"])

# 4. Velocidade do Vento
elif aba == "🌬️ Velocidade do Vento":
    st.title("🌬️ Velocidade do Vento")
    st.area_chart(df.set_index("cidade")["velocidade_vento"])

# 5. Condição do Clima
elif aba == "🌦️ Condição do Clima":
    st.title("🌦️ Clima Atual por Cidade")
    clima = df[["cidade", "descricao_clima"]].drop_duplicates()
    st.table(clima)
