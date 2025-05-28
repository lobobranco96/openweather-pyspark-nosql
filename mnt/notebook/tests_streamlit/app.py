import streamlit as st
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv
import os
import datetime
import time
import plotly.express as px

# Carrega variáveis de ambiente
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Conexão com MongoDB
client = MongoClient(MONGO_URI)
db = client["clima"]
collection = db["dados"]

# Cache com expiração automática
@st.cache_data(ttl=60)
def carregar_dados():
    dados = list(collection.find())
    df = pd.DataFrame(dados)
    if not df.empty:
        df["_id"] = df["_id"].astype(str)
        df["data_coleta"] = pd.to_datetime(df["data_coleta"], errors="coerce")
        df["data_hora"] = pd.to_datetime(df["data_hora"], errors="coerce")
    return df

st.set_page_config(page_title="🌤️ Dashboard Climático", layout="wide")

st.sidebar.markdown("⏱️ Dados atualizados automaticamente a cada 60 segundos.")
st.sidebar.markdown("🔄 Clique no botão abaixo para forçar uma atualização.")
if st.sidebar.button("🔄 Atualizar agora"):
    st.cache_data.clear()
    st.experimental_rerun()

# Dados carregados
df = carregar_dados()

if df.empty:
    st.error("❌ Nenhum dado encontrado no MongoDB.")
    st.stop()

# Mostra a última atualização
st.sidebar.markdown(f"🕒 Última atualização: `{datetime.datetime.now().strftime('%H:%M:%S')}`")

# Filtro por cidade
cidades_disponiveis = sorted(df["cidade"].unique())
cidades_selecionadas = st.sidebar.multiselect("📍 Filtrar por cidade:", cidades_disponiveis, default=cidades_disponiveis)
df = df[df["cidade"].isin(cidades_selecionadas)]

# Abas do menu
aba = st.sidebar.radio("📌 Selecione a aba", [
    "📍 Visão Geral",
    "🌡️ Temperatura por Cidade",
    "💧 Umidade",
    "🌬️ Velocidade do Vento",
    "🌦️ Condição do Clima",
    "📊 Insights Inteligentes"
])

# Aba 1 - Visão Geral
if aba == "📍 Visão Geral":
    st.title("📍 Visão Geral dos Dados Climáticos")
    st.dataframe(df[["cidade", "temperatura", "umidade", "descricao_clima", "data_hora"]])

# Aba 2 - Temperatura por Cidade
elif aba == "🌡️ Temperatura por Cidade":
    st.title("🌡️ Temperatura por Cidade")
    fig = px.line(df.sort_values("data_hora"), x="data_hora", y="temperatura", color="cidade",
                  title="Temperatura ao longo do tempo")
    st.plotly_chart(fig, use_container_width=True)

# Aba 3 - Umidade
elif aba == "💧 Umidade":
    st.title("💧 Umidade por Cidade")
    fig = px.line(df.sort_values("data_hora"), x="data_hora", y="umidade", color="cidade",
                  title="Umidade ao longo do tempo")
    st.plotly_chart(fig, use_container_width=True)

# Aba 4 - Velocidade do Vento
elif aba == "🌬️ Velocidade do Vento":
    st.title("🌬️ Velocidade do Vento por Cidade")
    fig = px.line(df.sort_values("data_hora"), x="data_hora", y="velocidade_vento", color="cidade",
                  title="Vento ao longo do tempo")
    st.plotly_chart(fig, use_container_width=True)

# Aba 5 - Condição do Clima
elif aba == "🌦️ Condição do Clima":
    st.title("🌦️ Condições Climáticas Atuais")
    clima = df.sort_values("data_hora", ascending=False).drop_duplicates("cidade")[["cidade", "descricao_clima", "temperatura"]]
    st.table(clima)

# Aba 6 - Insights Inteligentes
elif aba == "📊 Insights Inteligentes":
    st.title("📊 Insights Inteligentes com Base nos Dados Coletados")

    mais_quente = df.loc[df["temperatura"].idxmax()]
    mais_fria = df.loc[df["temperatura"].idxmin()]
    mais_umida = df.loc[df["umidade"].idxmax()]
    mais_vento = df.loc[df["velocidade_vento"].idxmax()]

    st.markdown(f"🔥 **Cidade mais quente:** `{mais_quente['cidade']}` com **{mais_quente['temperatura']}°C**")
    st.markdown(f"❄️ **Cidade mais fria:** `{mais_fria['cidade']}` com **{mais_fria['temperatura']}°C**")
    st.markdown(f"💧 **Maior umidade:** `{mais_umida['cidade']}` com **{mais_umida['umidade']}%**")
    st.markdown(f"🌬️ **Maior vento:** `{mais_vento['cidade']}` com **{mais_vento['velocidade_vento']} km/h**")

    clima_freq = df["descricao_clima"].value_counts().reset_index()
    clima_freq.columns = ["Clima", "Frequência"]
    st.bar_chart(clima_freq.set_index("Clima"))
